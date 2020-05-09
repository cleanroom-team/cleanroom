# -*- coding: utf-8 -*-
"""pkg_avahi command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class PkgAvahiCommand(Command):
    """The pkg_avahi command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "pkg_avahi",
            help_string="Setup MDNS using avahi.",
            file=__file__,
            **services
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
        self._execute(location, system_context, "pacman", "avahi")

        # Do setup:
        # Fix missing symlink:
        self._execute(
            location.next_line(),
            system_context,
            "symlink",
            "avahi-daemon.service",
            "dbus-org.freedesktop.Avahi.service",
            work_directory="/usr/lib/systemd/system",
        )

        # enable the daemon (actually set up socket activation)
        self._execute(
            location.next_line(),
            system_context,
            "systemd_enable",
            "avahi-daemon.service",
        )

        # Open the firewall for it:
        self._execute(
            location.next_line(),
            system_context,
            "net_firewall_open_port",
            "5353",
            protocol="udp",
            comment="Avahi",
        )

        # Edit /etc/nsswitch.conf:
        self._execute(
            location.next_line(),
            system_context,
            "sed",
            "/^hosts\\s*:/ s/resolve/mdns_minimal " "[NOTFOUND=return] resolve/",
            "/etc/nsswitch.conf",
        )
