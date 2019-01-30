# -*- coding: utf-8 -*-
"""add_hook command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import typing


class AddHookCommand(Command):
    """The add_hook command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('add_hook', syntax='<HOOK_NAME> <COMMAND> '
                         '<ARGS>* [message=<MESSAGE>] [<KWARGS>]',
                         help_string='Add a hook running command with arguments.',
                         file=__file__)

    def validate_arguments(self, location: Location,
                           *args: typing.Any, **kwargs: typing.Any) -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_args_at_least(location, 1,
                                     '"{}" needs a hook name and a '
                                     'command and optional arguments.', *args)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        location.set_description(kwargs.get('message', ''))
        system_context.add_hook(location, *args, **kwargs)
