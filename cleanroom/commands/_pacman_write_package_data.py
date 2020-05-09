# -*- coding: utf-8 -*-
"""_pacman_write_package_data command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.helper.archlinux.pacman import pacman_report
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class PacmanWritePackageDataCommand(Command):
    """The pacman command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_pacman_write_package_data",
            help_string="Write pacman package data into the filesystem.",
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
        pacman_report(
            system_context,
            system_context.file_name("/usr/lib/pacman"),
            pacman_command=self._binary(Binaries.PACMAN),
        )
