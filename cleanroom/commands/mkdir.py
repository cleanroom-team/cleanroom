"""mkdir command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file


class MkdirCommand(cmd.Command):
    """The mkdir command."""

    def __init__(self):
        """Constructor."""
        super().__init__('mkdir <DIRNAME> [<DIRNAME>][user=uid] [group=gid]',
                         'Create a new directory.')

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 1:
            raise ex.ParseError('mkdir needs a directory to create.',
                                file_name=file_name, line_number=line_number)

        return None

    def __call__(self, file_name, line_number, run_context, *args, **kwargs):
        """Execute command."""
        file.makedirs(run_context, *args, **kwargs)
