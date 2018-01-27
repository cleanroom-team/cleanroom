"""Image command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex

import re


class ImageCommand(cmd.Command):
    """The image command."""

    def __init__(self, ctx):
        """Constructor."""
        super().__init__()
        self._ctx = ctx

    def validate_arguments(self, line_number, args):
        """Validate the arguments."""
        name = None
        base = None

        if len(args) == 1:
            name = args[0]
        elif len(args) == 3:
            name = args[0]
            if args[1] != 'based_on':
                raise ex.ParseError(line_number,
                                    'Invalid syntax: Expected "based_on" '
                                    'as separater between name and base, '
                                    'got "{}".'.format(args[1]))
            base = args[2]
        else:
            raise ex.ParseError(line_number,
                                'Image needs a name and an optional '
                                'base image.')

        image_pattern = re.compile("^[A-Za-z][A-Za-z0-9_-]*$")
        if not image_pattern.match(name):
            raise ex.ParseError(line_number, 'Invalid name.')

        if not image_pattern.match(base):
            raise ex.ParseError(line_number, 'Invalid base.')

        return base

    def execute(self, *args):
        """Execute the command."""
        super().execute(*args)
