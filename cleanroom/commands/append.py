# -*- coding: utf-8 -*-
"""append command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.helper.generic.file as file


class AppendCommand(cmd.Command):
    """The append command."""

    def __init__(self):
        """Constructor."""
        super().__init__('append', syntax='<FILENAME> <CONTENTS>',
                         help='Append contents to file.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        return self._validate_arguments_exact(location, 2,
                                              '"{}" needs a file and contents '
                                              'to append to it.', *args)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        to_write = system_context.substitute(args[1]).encode('utf-8')
        file.append_file(system_context, args[0], to_write, **kwargs)
