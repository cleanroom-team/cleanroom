# -*- coding: utf-8 -*-
"""sed command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command


class SedCommand(Command):
    """The sed command."""

    def __init__(self):
        """Constructor."""
        super().__init__('sed', syntax='<PATTERN> <FILE>',
                         help='Run sed on a file.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_arguments_exact(location, 2,
                                       '"{}" needs a pattern and a file.',
                                       *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        system_context.run('/usr/bin/sed', '-i', '-e', args[0],
                           system_context.file_name(args[1]), outside=True)
