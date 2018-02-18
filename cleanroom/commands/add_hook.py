"""add_hook command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.parser as parser


class AddHookCommand(cmd.Command):
    """The add_hook command."""

    def __init__(self):
        """Constructor."""
        super().__init__('add_hook <HOOK_NAME> <MESSAGE> <COMMAND> '
                         '[<ARGS>] [<KWARGS>]',
                         'Add a hook running command with arguments.')
        self._file_name = ''
        self._line_number = -1

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        self._file_name = file_name
        self._line_number = line_number

        if len(args) < 2:
            raise ex.ParseError('add_hook needs a hook name and a command '
                                'with optional arguments',
                                file_name=file_name, line_number=line_number)

        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        hook = args[0]
        message = args[1]
        cmd = args[2]
        cmd_args = args[3:]
        cmd_kwargs = kwargs

        run_context.add_hook(hook, parser.Parser.create_execute_object(
            self._file_name, self._line_number,
            cmd, *cmd_args, message=message, **cmd_kwargs))
