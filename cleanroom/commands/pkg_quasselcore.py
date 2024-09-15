# -*- coding: utf-8 -*-
"""pkg_quasselcore command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class PkgQuasselcoreCommand(Command):
    """The pkg_quasselcore command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "pkg_quasselcore",
            help_string="Setup quasselcore.",
            file=__file__,
            **services,
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
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        self._execute(
            location, system_context, "pacman", "quassel-core", "postgresql-libs"
        )
        self._execute(
            location.next_line(),
            system_context,
            "systemd_harden_unit",
            "quassel.service",
        )
        self._execute(
            location.next_line(), system_context, "systemd_enable", "quassel.service"
        )

        self._execute(
            location.next_line(),
            system_context,
            "net_firewall_open_port",
            4242,
            protocol="tcp",
            comment="Quassel",
        )
