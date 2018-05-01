# -*- coding: utf-8 -*-
"""chmod command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.helper.generic.file as file


class ChmodCommand(cmd.Command):
    """The chmod command."""

    def __init__(self):
        """Constructor."""
        super().__init__('chmod', syntax='<MODE> <FILE>+',
                         help='Chmod a file or files.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_arguments_at_least(location, 2,
                                          '"{}" takes a moda and one '
                                          'or more files.', *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        file.chmod(system_context, *args, **kwargs)
