# -*- coding: utf-8 -*-
"""swupd command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.exceptions import GenerateError, ParseError
from cleanroom.location import Location
from cleanroom.helper.run import run
from cleanroom.systemcontext import SystemContext

import typing


class swupdCommand(Command):
    """The swupd command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "swupd",
            target_distribution="clr",
            syntax="<PACKAGES> [remove=False]",
            help_string="Run swupd to install <PACKAGES>.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        if not self._binary(Binaries.SWUPD):
            raise ParseError("No swupd binary was found.")

        self._validate_args_at_least(
            location, 1, '"{}" needs at least one package or group to install.', *args
        )
        self._validate_kwargs(location, ("remove",), **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        # Validate:
        if system_context.substitution("CLRM_PACKAGE_TYPE", "") != "swupd":
            raise GenerateError(
                "Trying to run swupd when other package type has been initialized before."
            )

        op = "bundle-rm" if kwargs.get("remove", False) else "bundle-add"

        run(
            self._binary(Binaries.SWUPD),
            op,
            f"--path={system_context.fs_directory}",
            *args,
        )
