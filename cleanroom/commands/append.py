# -*- coding: utf-8 -*-
"""append command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.helper.file import append_file
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class AppendCommand(Command):
    """The append command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "append",
            syntax="<FILENAME> <CONTENTS>",
            help_string="Append contents to file.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_arguments_exact(
            location, 2, '"{}" needs a file and contents ' "to append to it.", *args
        )
        self._validate_kwargs(location, ("force",), **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        to_write = args[1].encode("utf-8")
        append_file(system_context, args[0], to_write, **kwargs)
