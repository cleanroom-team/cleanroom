# -*- coding: utf-8 -*-
"""remove command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.helper.generic.file as file


class RemoveCommand(cmd.Command):
    """The copy command."""

    def __init__(self):
        """Constructor."""
        super().__init__('remove',
                         syntax='<FILE_LIST> [force=True] [recursive=True]',
                         help='remove files within the system.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_at_least(location, 1,
                                     '"{}" needs at least one file or '
                                     'directory to remove.', *args)
        self._validate_kwargs(location, ('force', 'recursive'), **kwargs)
        return None

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        file.remove(system_context, *args, **kwargs)
