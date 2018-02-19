"""append command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file


class AppendCommand(cmd.Command):
    """The append command."""

    def __init__(self):
        """Constructor."""
        super().__init__('append <FILENAME> <CONTENTS>',
                         'Append contents to file.')

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 2:
            raise ex.ParseError('append needs a file and contents to append.',
                                file_name=file_name, line_number=line_number)

        return None

    def __call__(self, file_name, line_number, run_context, *args, **kwargs):
        """Execute command."""
        to_write = run_context.substitute(args[1]).encode('utf-8')
        file.append_file(run_context, args[0], to_write, **kwargs)
