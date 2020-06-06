# -*- coding: utf-8 -*-
"""pkg_usbguard command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.helper.file import create_file, makedirs, remove, move
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import textwrap
import typing


class PkgAvahiCommand(Command):
    """The pkg_usbguard command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "pkg_usbguard", help_string="Install usbguard", file=__file__, **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        self._execute(location, system_context, "pacman", "usbguard")

        # Do setup:
        # enable the daemon (actually set up socket activation)
        self._execute(
            location.next_line(),
            system_context,
            "systemd_enable",
            "usbguard-dbus.service",
        )

        create_file(
            system_context,
            "/usr/lib/tmpfiles.d/usbguard.conf",
            textwrap.dedent(
                """\
                    d /var/log/usbguard 0750 root root - -

                    d /var/etc/usbguard 0750 root root - -
                    C /var/etc/usbguard - - - - -
                    """
            ).encode("utf-8"),
        )

        self._execute(
            location.next_line(),
            system_context,
            "sed",
            "/RuleFile=\\/etc/ cRuleFile=/var/etc/usbguard/rules.conf",
            "/etc/usbguard/usbguard-daemon.conf",
        )
        self._execute(
            location.next_line(),
            system_context,
            "sed",
            "/IPCAccessControlFiles=\\/etc/ cIPCAccessControlFiles=/var/etc/usbguard/IPCAccessControl.d",
            "/etc/usbguard/usbguard-daemon.conf",
        )
        self._execute(
            location.next_line(),
            system_context,
            "sed",
            "/ImplicitPolicyTarget=/ cImplicitPolicyTarget=allow",
            "/etc/usbguard/usbguard-daemon.conf",
        )

        makedirs(
            system_context, "/usr/share/factory/var/etc/usbguard/IPCaccessControl.d"
        )
        move(
            system_context,
            "/etc/usbguard/usbguard-daemon.conf",
            "/usr/share/factory/var/etc/usbguard",
        )
        create_file(
            system_context,
            "/usr/share/factory/var/etc/usbguard/rules.conf",
            b"",
            mode=0o600,
        )

        remove(
            system_context, "/etc/usbguard", recursive=True,
        )

        # Fix for https://github.com/USBGuard/usbguard/issues/287
        makedirs(system_context, "/usr/lib/systemd/system/usbguard.service.d")
        create_file(
            system_context,
            "/usr/lib/systemd/system/usbguard.service.d/bugfix.conf",
            textwrap.dedent(
                """\
                [Service]
                CapabilityBoundingSet=CAP_DAC_OVERRIDE
                ReadWritePaths=-/var/etc/usbguard/rules.conf
                ExecStart=
                ExecStart=/usr/bin/usbguard-daemon -k -c /var/etc/usbguard/usbguard-daemon.conf
                """
            ).encode("utf-8"),
        )
