# -*- coding: utf-8 -*-
"""mkdir command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.helper.generic.file as file


class MkdirCommand(cmd.Command):
    """The mkdir command."""

    def __init__(self):
        """Constructor."""
        super().__init__('mkdir',
                         syntax='<DIRNAME> [<DIRNAME>] [user=uid] [group=gid]',
                         help='Create a new directory.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_at_least(location, 1,
                                     '"{}" needs at least one directory '
                                     'to create.', *args)
        self._validate_kwargs(location, ('user', 'group'), **kwargs)
        return None

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        file.makedirs(system_context, *args, **kwargs)
