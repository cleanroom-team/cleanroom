# -*- coding: utf-8 -*-
"""move command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file


class MoveCommand(cmd.Command):
    """The move command."""

    def __init__(self):
        """Constructor."""
        super().__init__('move', syntax='<SOURCE> [<SOURCE>] <DEST> ',
                         help='Move file or directory.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        if len(args) < 2:
            raise ex.ParseError('move needs source and a destination.',
                                location=location)
        if kwargs.get('from_outside', False) \
           and kwargs.get('to_outside', False):
            raise ex.ParseError('You can not move a file from_outside '
                                'to_outside.', location=location)
        return None

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        file.move(system_context, *args, **kwargs)
