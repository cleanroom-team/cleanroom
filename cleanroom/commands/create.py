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

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 2:
            raise ex.ParseError(file_name, line_number,
                                'create_file needs a file and its contents.')

        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        file.create_file(run_context, args[0], args[1].encode('utf-8'),
                         **kwargs)
