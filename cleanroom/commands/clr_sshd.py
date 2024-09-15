# -*- coding: utf-8 -*-
"""clr_sshd command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.command import Command
from cleanroom.helper.file import create_file, exists
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing
import textwrap


class PkgSshdCommand(Command):
    """The clr_sshd command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "clr_sshd",
            syntax="[AllowTcpForwading=False] [GatewayPorts=False]",
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
            (
                "AllowTcpForwarding",
                "GatewayPorts",
            ),
            **kwargs,
        )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        self._install_openssh(location, system_context)
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
        self._execute(location, system_context, "swupd", "openssh-server")

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
