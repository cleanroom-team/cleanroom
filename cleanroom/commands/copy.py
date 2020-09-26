# -*- coding: utf-8 -*-
"""copy command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.exceptions import ParseError
from cleanroom.helper.file import copy
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class CopyCommand(Command):
    """The copy command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "copy",
            syntax="<SOURCE>+ <DEST> [ignore_missing=False] "
            "[from_outside=True] [to_outside=True] "
            "[recursive=False] [force=False]",
            help_string="Copy a file within the system.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_args_at_least(
            location, 2, '"{}" needs one or more sources and a ' "destination", *args
        )
        self._validate_kwargs(
            location,
            ("from_outside", "to_outside", "ignore_missing", "recursive", "force"),
            **kwargs,
        )

        if kwargs.get("from_outside", False) and kwargs.get("to_outside", False):
            raise ParseError(
                f'You can not "{self.name}" a file from_outside to_outside.',
                location=location,
            )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        copy(system_context, *args, **kwargs)
