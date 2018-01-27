"""Based command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex

import re


class BasedCommand(cmd.Command):
    """The basedOn command."""

    def __init__(self, ctx):
        """Constructor."""
        super().__init__("based (on <SYSTEM_NAME>)",
                         "Use <SYSTEM_NAME> as a base for this system.\n\n"
                         "Note: This command needs to be the first in the\n"
                         "system definition file!")
        self._ctx = ctx

    def validate_arguments(self, line_number, args):
        """Validate the arguments."""
        base = None

        if len(args) == 0:
            raise ex.ParseError(line_number,
                                '"based" needs a system name.')
        elif len(args) == 1:
            base = args[0]
        elif len(args) == 2:
            if args[0] != 'on':
                raise ex.ParseError(line_number,
                                    '"based" may take an optional filler "on" '
                                    'as first argument.')
            else:
                base = args[1]
        else:
            raise ex.ParseError(line_number,
                                '"based" takes an optional filler "on" and '
                                'a system name. Too many arguments given.')

        assert(base)
        system_pattern = re.compile('^[A-Za-z][A-Za-z0-9_-]*$')
        if not system_pattern.match(base):
            raise ex.ParseError(line_number,
                                '"based" got invalid base system name "{}".'
                                .format(base))

        return base
