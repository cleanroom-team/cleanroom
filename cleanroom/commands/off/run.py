# -*- coding: utf-8 -*-
"""run command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import typing


class RunCommand(Command):
    """The run command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('run',
                         syntax='<COMMAND> [<ARGS>] [outside=False] '
                         '[shell=False] [returncode=0] [stdout=None] '
                         '[stderr=None]',
                         help_string='Run a command inside/outside of the '
                         'current system.', file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_args_at_least(location, 1,
                                     '"{}" needs a command to run and '
                                     'optional arguments.', *args)
        self._validate_kwargs(location, ('returncode', 'outside', 'shell',
                                         'stderr', 'stdout'),
                              **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        system_context.run(*args, **kwargs)
