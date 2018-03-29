# -*- coding: utf-8 -*-
"""sed command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.helper.generic.file as file


class SedCommand(cmd.Command):
    """The sed command."""

    def __init__(self):
        """Constructor."""
        super().__init__('sed', syntax='<PATTERN> <FILE>',
                         help='Run sed on a file.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        return self._validate_arguments_exact(location, 2,
                                              '"{}" needs a pattern and a '
                                              'file.', *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        pattern = args[0]
        f = file.file_name(system_context, args[1])

        system_context.run('/usr/bin/sed', '-i', '-e', pattern, f,
                           outside=True)
