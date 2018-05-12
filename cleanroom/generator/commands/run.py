# -*- coding: utf-8 -*-
"""run command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command


class RunCommand(Command):
    """The run command."""

    def __init__(self):
        """Constructor."""
        super().__init__('run',
                         syntax='<COMMAND> [<ARGS>] [outside=False] '
                         '[shell=False] [exit_code=0] [stdout=None] '
                         '[stderr=None]',
                         help='Run a command inside/outside of the '
                         'current system.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_at_least(location, 1,
                                     '"{}" needs a command to run and '
                                     'optional arguments.', *args)
        self._validate_kwargs(location, ('exit_code', 'outside', 'shell',
                                         'stderr', 'stdout'),
                              **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        system_context.run(*args, **kwargs)
