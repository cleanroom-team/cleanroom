"""Copy_Into command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file


class CopyIntoCommand(cmd.Command):
    """The copy_into Command."""

    def __init__(self):
        """Constructor."""
        super().__init__('copy_into <FILE> <LOCATION_INSIDE> [replace]',
                         'Copy a file into a system, optionally overwriting '
                         'an existing file.')

    def validate_arguments(self, line_number, args):
        """Validate the arguments."""
        if len(args) < 2:
            raise ex.ParseError(line_number,
                                'To few arguments for "copy_into". '
                                'Need <FILE> and <LOCATION_INSIDE> and '
                                '(optional) "replace".')
        elif len(args) == 2:
            return None
        elif len(args) == 3:
            if args[2] != 'replace':
                raise ex.ParseError(line_number,
                                    'Third (optional) argument must be '
                                    '"replace".')
        else:
            raise ex.ParseError(line_number, )

    def execute(self, run_context, args):
        """Execute command."""
        file.copy_into(run_context, args[0], args[1])
        return True
