"""run command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.run as run


class RunCommand(cmd.Command):
    """The run command."""

    def __init__(self):
        """Constructor."""
        super().__init__('run <COMMAND> [<ARGS>] [outside=False] '
                         '[shell=False]',
                         'Run a command inside/outside of the current system.')

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        if len(args) < 1:
            raise ex.ParseError(file_name, line_number,
                                'run needs a command to run and optional '
                                'arguments.')
        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        if kwargs.get('shell', 'False') == 'True':
            args = ('/usr/bin/bash', '-c', *args)
        if kwargs.get('outside', 'False') == 'False':
            kwargs['chroot'] = run_context.fs_directory()
        if kwargs.get('exit_code', 0) == 'None':
            kwargs['exit_code'] = None

        run.run(*args, **kwargs, trace_output=run_context.ctx.printer.trace)
