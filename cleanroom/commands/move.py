# -*- coding: utf-8 -*-
"""move command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.command import Command
from cleanroom.exceptions import ParseError
from cleanroom.helper.file import move
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class MoveCommand(Command):
    """The move command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "move",
            syntax="<SOURCE> [<SOURCE>] <DEST> "
            " [ignore_missing_sources=False]"
            " [from_outside=False] [to_outside=False] "
            "[force=False]",
            help_string="Move file or directory.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_args_at_least(
            location, 2, '"{}" needs at least one ' "source and a destination.", *args
        )
        self._validate_kwargs(
            location,
            ("from_outside", "to_outside", "ignore_missing_sources", "force"),
            **kwargs,
        )
        if kwargs.get("from_outside", False) and kwargs.get("to_outside", False):
            raise ParseError(
                "You can not move a file from_outside to_outside.", location=location
            )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        move(system_context, *args, **kwargs)
