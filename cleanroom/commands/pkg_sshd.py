# -*- coding: utf-8 -*-
"""pkg_sshd command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.helper.file import create_file, exists
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os.path
import typing
import textwrap


class PkgSshdCommand(Command):
    """The pkg_sshd command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "pkg_sshd",
            syntax="[AllowTcpForwading=False] [GatewayPorts=False] [PermitRootLogin=False]",
            help_string="Install sshd. Please add host keys into /etc/ssh",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_no_args(location, *args)
        self._validate_kwargs(
            location,
            ("AllowTcpForwarding", "GatewayPorts", "PermitRootLogin"),
            **kwargs,
        )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        self._install_openssh(location, system_context)
        self._harden_sshd(location, system_context, **kwargs)
        self._execute(
            location.next_line(), system_context, "systemd_enable", "sshd.service"
        )

        self._execute(
            location.next_line(),
            system_context,
            "net_firewall_open_port",
            22,
            protocol="tcp",
            comment="sshd",
        )

        self._persistent_known_hosts(location.next_line(), system_context)

    def _install_openssh(
        self, location: Location, system_context: SystemContext
    ) -> None:
        self._execute(location, system_context, "pacman", "openssh")

    def _yes_or_no(self, arg: str, **kwargs: typing.Any) -> str:
        if kwargs.get(arg, False):
            return "yes"
        return "no"

    def _set_sshd_config_yes_or_no(
        self,
        location: Location,
        system_context: SystemContext,
        arg: str,
        **kwargs: typing.Any
    ) -> None:
        self._set_sshd_config(
            location, system_context, arg, self._yes_or_no(arg, **kwargs)
        )

    def _harden_sshd(
        self, location: Location, system_context: SystemContext, **kwargs: typing.Any
    ) -> None:
        # Install custom moduli
        moduli = os.path.join(self._config_directory(system_context), "moduli")
        if os.path.exists(moduli):
            self._execute(
                location.next_line(),
                system_context,
                "copy",
                moduli,
                "/etc/ssh/moduli",
                from_outside=True,
                force=True,
            )

        # Config tweaks:
        self._set_sshd_config_yes_or_no(
            location, system_context, "PermitRootLogin", **kwargs,
        )
        self._set_sshd_config(location, system_context, "PasswordAuthentication", "no")
        self._set_sshd_config(location, system_context, "PermitEmptyPasswords", "no")
        self._set_sshd_config(location, system_context, "Protocol", "2")

        self._set_sshd_config_yes_or_no(
            location, system_context, "AllowTcpForwarding", **kwargs
        )
        self._set_sshd_config_yes_or_no(
            location, system_context, "GatewayPorts", **kwargs
        )
        self._set_sshd_config(location, system_context, "X11Forwarding", "no")

        self._set_sshd_config(
            location, system_context, "HostKey", "/etc/ssh/ssh_host_ed25519_key"
        )

    def _set_sshd_config(
        self, location: Location, system_context: SystemContext, key: str, value: str
    ) -> None:
        self._execute(
            location.next_line(),
            system_context,
            "sed",
            "/^[\\s#]*{0}\\s/ c{0} {1}".format(key, value),
            "/etc/ssh/sshd_config",
        )

    def _persistent_known_hosts(
        self, location: Location, system_context: SystemContext
    ) -> None:
        if not exists(system_context, "/usr/lib/tmpfiles.d/ssh.conf"):
            create_file(
                system_context,
                "/usr/lib/tmpfiles.d/ssh.conf",
                textwrap.dedent(
                    """\
                    d /var/etc/ssh 644 root root - -
                    f /var/etc/ssh/ssh_known_hosts 644 root root -
                    L /etc/ssh/ssh_known_hosts - - - - /var/etc/ssh/ssh_known_hosts
                    """
                ).encode("utf-8"),
                mode=0o644,
            )
