# -*- coding: utf-8 -*-
"""mkdir command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
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
        if len(args) < 1:
            raise ex.ParseError('mkdir needs a directory to create.',
                                location=location)
        return None

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        file.makedirs(system_context, *args, **kwargs)
