# -*- coding: utf-8 -*-
"""remove command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.helper.file import remove
from cleanroom.systemcontext import SystemContext

import typing


class RemoveCommand(Command):
    """The copy command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "remove",
            syntax="<FILE_LIST> [force=True] [recursive=True] [outside=False]",
            help_string="remove files within the system.",
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
            '"{}" needs at least one file or ' "directory to remove.",
            *args
        )
        self._validate_kwargs(location, ("force", "recursive", "outside"), **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        remove(system_context, *args, **kwargs)
