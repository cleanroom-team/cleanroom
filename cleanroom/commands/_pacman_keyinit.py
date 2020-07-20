# -*- coding: utf-8 -*-
"""_pacman_keyinit command

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext
from cleanroom.helper.run import run

import typing


class PacstrapCommand(Command):
    """The pacstrap command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_pacman_keyinit",
            syntax="<PACKAGES> pacman_key=<path_to_binary> "
            "gpg_dir=<path_to_gpg_dir>",
            help_string="Enable extra setup for the pacman keyring.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_no_args(location, *args)
        self._validate_kwargs(location, ("pacman_key", "gpg_dir"), **kwargs)
        self._require_kwargs(location, ("gpg_dir", "gpg_dir"), **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""

        pacman_key_command = kwargs.get("pacman_key", "")
        gpg_dir = kwargs.get("gpg_dir", "")

        run(
            pacman_key_command,
            "--populate",
            "archlinux",
            "--gpgdir",
            gpg_dir,
            work_directory=system_context.systems_definition_directory,
        )
