"""add_hook command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex


class AddHookCommand(cmd.Command):
    """The add_hook command."""

    def __init__(self):
        """Constructor."""
        super().__init__('add_hook <HOOK_NAME> <MESSAGE> <COMMAND> '
                         '[<ARGS>] [<KWARGS>]',
                         'Add a hook running command with arguments.')

    def validate_arguments(self, run_context, *args, **kwargs):
        """Validate the arguments."""
        if len(args) < 2:
            raise ex.ParseError('add_hook needs a hook name and a command '
                                'with optional arguments',
                                run_context=run_context)

        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        hook = args[0]
        message = args[1]
        cmd = args[2]
        cmd_args = args[3:]
        cmd_kwargs = kwargs

        run_context.add_hook(hook, cmd, *cmd_args, message=message,
                             **cmd_kwargs)
