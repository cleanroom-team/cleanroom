"""remove command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file


class RemoveCommand(cmd.Command):
    """The copy command."""

    def __init__(self):
        """Constructor."""
        super().__init__('remove <FILE_LIST> [force=True] [recursive=True]',
                         'remove files within the system.')

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        if len(args) == 0:
            raise ex.ParseError('remove needs a list of files to remove',
                                file_name=file_name, line_number=line_number)

        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        file.remove(run_context, *args, **kwargs)
