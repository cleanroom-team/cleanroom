# -*- coding: utf-8 -*-
"""remove command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
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
        if len(args) == 0:
            raise ex.ParseError('remove needs a list of files to remove',
                                location=location)
        return None

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        file.remove(system_context, *args, **kwargs)
