# -*- coding: utf-8 -*-
"""append command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.file import append_file


class AppendCommand(Command):
    """The append command."""

    def __init__(self):
        """Constructor."""
        super().__init__('append', syntax='<FILENAME> <CONTENTS>',
                         help='Append contents to file.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_arguments_exact(location, 2,
                                       '"{}" needs a file and contents '
                                       'to append to it.', *args)
        self._validate_kwargs(location, ('force'), **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        to_write = system_context.substitute(args[1]).encode('utf-8')
        append_file(system_context, args[0], to_write, **kwargs)
