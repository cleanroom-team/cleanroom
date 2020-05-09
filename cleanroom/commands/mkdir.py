# -*- coding: utf-8 -*-
"""mkdir command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.helper.file import makedirs
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class MkdirCommand(Command):
    """The mkdir command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "mkdir",
            syntax="<DIRNAME>+ [user=uid] [group=gid] " "[mode=0o755] [force=False]",
            help_string="Create a new directory.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_args_at_least(
            location, 1, '"{}" needs at least one directory ' "to create.", *args
        )
        self._validate_kwargs(location, ("user", "group", "mode", "force"), **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        makedirs(system_context, *args, **kwargs)
