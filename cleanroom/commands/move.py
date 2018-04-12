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
        super().__init__('move', syntax='<SOURCE> [<SOURCE>] <DEST> '
                         ' [ignore_missing_sources=False]'
                         ' [from_outside=False] [to_outside=False]',
                         help='Move file or directory.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_at_least(location, 2,
                                     '"{}" needs at least one '
                                     'source and a destination.', *args)
        self._validate_kwargs(location, ('from_outside', 'to_outside',
                                         'ignore_missing_sources'),
                              **kwargs)
        if kwargs.get('from_outside', False) \
           and kwargs.get('to_outside', False):
            raise ex.ParseError('You can not move a file from_outside '
                                'to_outside.', location=location)
        return None

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        file.move(system_context, *args, **kwargs)
