# -*- coding: utf-8 -*-
"""add_hook command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class AddHookCommand(Command):
    """The add_hook command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "add_hook",
            syntax="<HOOK_NAME> <COMMAND> " "<ARGS>* [message=<MESSAGE>] [<KWARGS>]",
            help_string="Add a hook running command with " "arguments.",
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
            '"{}" needs a hook name and a ' "command and optional arguments.",
            *args
        )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        message: str = "",
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        location.set_description(message)
        self._add_hook(location, system_context, args[0], args[1], *args[2:], **kwargs)
