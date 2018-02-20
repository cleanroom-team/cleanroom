"""sed command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file


class SedCommand(cmd.Command):
    """The sed command."""

    def __init__(self):
        """Constructor."""
        super().__init__('sed <PATTERN> <FILE>',
                         'Run sed on a file.')

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 2:
            raise ex.ParseError('sed needs a pattern and a file.',
                                file_name=file_name, line_number=line_number)

        return None

    def __call__(self, file_name, line_number, run_context, *args, **kwargs):
        """Execute command."""
        pattern = args[0]
        f = file.file_name(run_context, args[1])

        run_context.run('/usr/bin/sed', '-i', '-e', pattern, f, outside=True)
