"""create command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file


class CreateCommand(cmd.Command):
    """The create command."""

    def __init__(self):
        """Constructor."""
        super().__init__('create <FILENAME> <CONTENTS> [force=True]',
                         'Create a file with contents.')

    def validate_arguments(self, run_context, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 2:
            raise ex.ParseError('create_file needs a file and its contents.',
                                run_context=run_context)

        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        to_write = run_context.substitute(args[1]).encode('utf-8')
        file.create_file(run_context, args[0], to_write, **kwargs)
