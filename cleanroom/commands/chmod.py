# -*- coding: utf-8 -*-
"""chmod command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.helper.file import chmod
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class ChmodCommand(Command):
    """The chmod command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "chmod",
            syntax="<MODE> <FILE>+",
            help_string="Chmod a file or files.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_arguments_at_least(
            location, 2, '"{}" takes a mode and one ' "or more files.", *args, **kwargs
        )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        chmod(system_context, *args, **kwargs)
