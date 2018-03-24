# -*- coding: utf-8 -*-
"""run command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex


class RunCommand(cmd.Command):
    """The run command."""

    def __init__(self):
        """Constructor."""
        super().__init__('run',
                         syntax='<COMMAND> [<ARGS>] [outside=False] '
                         '[shell=False]',
                         help='Run a command inside/outside of the '
                         'current system.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        if len(args) < 1:
            raise ex.ParseError('run needs a command to run and optional '
                                'arguments.', location=location)
        return None

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        args = map(lambda a: system_context.substitute(a), args)

        stdout = kwargs.get('stdout', None)
        if stdout is not None:
            stdout = system_context.substitute(stdout)
        kwargs['stdout'] = stdout

        stderr = kwargs.get('stderr', None)
        if stderr is not None:
            stderr = system_context.substitute(stderr)
        kwargs['stderr'] = stderr

        system_context.run(*args, **kwargs)
