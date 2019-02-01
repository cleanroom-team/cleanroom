# -*- coding: utf-8 -*-
"""set command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.command import Command
from cleanroom.systemcontext import SystemContext

import typing


class SetDefaultTargetCommand(Command):
    """The set command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__('set', syntax='<KEY> <VALUE> [local=True]',
                         help_string='Set up a substitution.', file=__file__,
                         **services)

    def validate(self, location: Location,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Validate the arguments."""
        self._validate_arguments_exact(location, 2,
                                       '"{}" needs a key and a value.',
                                       *args, **kwargs)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        system_context.set_substitution(args[0], args[1])
