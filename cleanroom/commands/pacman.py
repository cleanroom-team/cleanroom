# -*- coding: utf-8 -*-
"""pacman command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.helper.archlinux.pacman import pacman
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class PacmanCommand(Command):
    """The pacman command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "pacman",
            syntax="<PACKAGES> [remove=False] "
            "[overwrite=GLOB] [assume_installed=PKG]",
            help_string="Run pacman to install <PACKAGES>.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_args_at_least(
            location,
            1,
            '"{}"" needs at least ' "one package or group to install.",
            *args
        )
        self._validate_kwargs(
            location, ("remove", "overwrite", "assume_installed",), **kwargs
        )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        pacman(
            system_context,
            *args,
            remove=kwargs.get("remove", False),
            overwrite=kwargs.get("overwrite", ""),
            assume_installed=kwargs.get("assume_installed", ""),
            pacman_command=self._binary(Binaries.PACMAN),
            chroot_helper=self._binary(Binaries.CHROOT_HELPER)
        )
