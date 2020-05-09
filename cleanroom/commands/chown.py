# -*- coding: utf-8 -*-
"""chown command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.helper.file import chown
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class ChownCommand(Command):
    """The chown command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "chown",
            syntax="<FILE>+ [user=<USER>] [group=<GROUP>] " "[recursive=False]",
            help_string="Chmod a file or files.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_args_at_least(
            location, 1, '"{}" takes one or more files.', *args
        )
        self._validate_kwargs(location, ("user", "group", "recursive",), **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        chown(
            system_context,
            kwargs.get("user", "root"),
            kwargs.get("group", "root"),
            *args,
            recursive=kwargs.get("recursive", False)
        )
