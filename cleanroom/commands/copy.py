# -*- coding: utf-8 -*-
"""copy command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file


class CopyCommand(cmd.Command):
    """The copy command."""

    def __init__(self):
        """Constructor."""
        super().__init__('copy',
                         syntax='<SOURCE> [<SOURCE>] <DEST> [force=True] '
                         '[from_outside=True] [to_outside=True]',
                         help='Copy a file within the system.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        if len(args) < 2:
            raise ex.ParseError('copy needs source and a destination.',
                                location=location)

        if kwargs.get('from_outside', False) \
           and kwargs.get('to_outside', False):
            raise ex.ParseError('You can not copy a file from_outside '
                                'to_outside.', location=location)
        return None

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        file.copy(system_context, *args, **kwargs)
