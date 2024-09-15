# -*- coding: utf-8 -*-
"""systemd_enable command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.helper.systemd import systemd_enable
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class SystemdEnableCommand(Command):
    """The systemd_enable command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "systemd_enable",
            syntax="<UNIT> [<MORE_UNITS>] [user=False]",
            help_string="Enable systemd units.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_args_at_least(
            location, 1, '"{}" needs at least one ' "unit to enable.", *args
        )
        self._validate_kwargs(location, ("user",), **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        systemd_enable(
            system_context,
            *args,
            systemctl_command=self._binary(Binaries.SYSTEMCTL),
            **kwargs,
        )
