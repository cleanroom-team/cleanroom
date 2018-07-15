# -*- coding: utf-8 -*-
"""chmod command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.file import chmod


class ChmodCommand(Command):
    """The chmod command."""

    def __init__(self):
        """Constructor."""
        super().__init__('chmod', syntax='<MODE> <FILE>+',
                         help='Chmod a file or files.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_arguments_at_least(location, 2,
                                          '"{}" takes a mode and one '
                                          'or more files.', *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        chmod(system_context, *args, **kwargs)