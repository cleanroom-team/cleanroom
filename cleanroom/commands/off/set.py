# -*- coding: utf-8 -*-
"""set command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import typing


class SetDefaultTargetCommand(Command):
    """The set command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('set', syntax='<KEY> <VALUE> [local=True]',
                         help_string='Set up a substitution.', file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_arguments_exact(location, 2,
                                       '"{}" needs a key and a value.',
                                       *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        key = args[0]
        value = args[1]

        system_context.set_substitution(key, value)
