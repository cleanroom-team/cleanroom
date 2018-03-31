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
                         syntax='<SOURCE>+ <DEST> [force=True] '
                         '[from_outside=True] [to_outside=True]',
                         help='Copy a file within the system.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_at_least(location, 2,
                                     '"{}" needs one or more sources and a '
                                     'destination', *args)
        self._validate_kwargs(location, ('from_outside', 'to_outside'),
                              **kwargs)

        if kwargs.get('from_outside', False) \
           and kwargs.get('to_outside', False):
            raise ex.ParseError('You can not "{}" a file from_outside '
                                'to_outside.'.format(self.name()),
                                location=location)
        return None

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        file.copy(system_context, *args, **kwargs)
