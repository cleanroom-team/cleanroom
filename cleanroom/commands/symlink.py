# -*- coding: utf-8 -*-
"""symlink command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.helper.generic.file as file


class SymlinkCommand(cmd.Command):
    """The symlink command."""

    def __init__(self):
        """Constructor."""
        super().__init__('symlink',
                         syntax='<SOURCE> <TARGET> [base_directory=BASE]',
                         help='Create a symlink.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_exact(location, 2,
                                  '"{}" needs a source and a target.', *args)
        self._validate_kwargs(location, ('base_directory',), **kwargs)
        return None

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        source = args[0]
        target = args[1]
        base = kwargs.get('base_directory', None)

        file.symlink(system_context, source, target, base_directory=base)
