# -*- coding: utf-8 -*-
"""remove command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.file import remove


class RemoveCommand(Command):
    """The copy command."""

    def __init__(self):
        """Constructor."""
        super().__init__('remove',
                         syntax='<FILE_LIST> [force=True] [recursive=True]',
                         help='remove files within the system.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_at_least(location, 1,
                                     '"{}" needs at least one file or '
                                     'directory to remove.', *args)
        self._validate_kwargs(location, ('force', 'recursive'), **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        remove(system_context, *args, **kwargs)
