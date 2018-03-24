# -*- coding: utf-8 -*-
"""symlink command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
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
        if len(args) != 2:
            raise ex.ParseError('symlink needs a source and a target.',
                                location=location)
        return None

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        source = args[0]
        target = args[1]
        base = kwargs.get('base_directory', None)

        file.symlink(system_context, source, target, base_directory=base)
