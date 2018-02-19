"""set command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex


class SetDefaultTargetCommand(cmd.Command):
    """The set command."""

    def __init__(self):
        """Constructor."""
        super().__init__('set <KEY> <VALUE> [local=True]',
                         'Set up a substitution.')

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 2:
            raise ex.ParseError('set needs a key and a value.',
                                file_name=file_name, line_number=line_number)

        return None

    def __call__(self, file_name, line_number, run_context, *args, **kwargs):
        """Execute command."""
        key = args[0]
        value = args[1]

        is_local = (kwargs.get('local', 'False') == 'True')

        run_context.set_substitution(key, value, local=is_local)
