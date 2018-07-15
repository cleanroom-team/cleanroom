# -*- coding: utf-8 -*-
"""copy command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.file import copy

from cleanroom.exceptions import ParseError


class CopyCommand(Command):
    """The copy command."""

    def __init__(self):
        """Constructor."""
        super().__init__('copy',
                         syntax='<SOURCE>+ <DEST> [ignore_missing=False] '
                         '[from_outside=True] [to_outside=True] '
                         '[recursive=False] [force=False]',
                         help='Copy a file within the system.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_at_least(location, 2,
                                     '"{}" needs one or more sources and a '
                                     'destination', *args)
        self._validate_kwargs(location, ('from_outside', 'to_outside',
                                         'ignore_missing', 'recursive',
                                         'force'),
                              **kwargs)

        if kwargs.get('from_outside', False) \
           and kwargs.get('to_outside', False):
            raise ParseError('You can not "{}" a file from_outside to_outside.'
                             .format(self.name()), location=location)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        copy(system_context, *args, **kwargs)