# -*- coding: utf-8 -*-
"""create command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.helper.generic.file as file


class CreateCommand(cmd.Command):
    """The create command."""

    def __init__(self):
        """Constructor."""
        super().__init__('create', syntax='<FILENAME> <CONTENTS> [force=True]',
                         help='Create a file with contents.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_exact(location, 2,
                                  '"{}" takes a file name and the contents '
                                  'to store in the file.', *args)
        self._validate_kwargs(location, ('force',), **kwargs)
        return None

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        to_write = system_context.substitute(args[1]).encode('utf-8')
        file.create_file(system_context, args[0], to_write, **kwargs)
