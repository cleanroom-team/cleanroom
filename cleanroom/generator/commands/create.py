# -*- coding: utf-8 -*-
"""create command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.file import create_file


class CreateCommand(Command):
    """The create command."""

    def __init__(self):
        """Constructor."""
        super().__init__('create', syntax='<FILENAME> <CONTENTS> [force=True] '
                         '[mode=0o644] [user=UID/name] [group=GID/name]',
                         help='Create a file with contents.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_exact(location, 2,
                                  '"{}" takes a file name and the contents '
                                  'to store in the file.', *args)
        self._validate_kwargs(location, ('force', 'mode', 'user', 'group'),
                              **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        file_name = args[0]
        to_write = system_context.substitute(args[1]).encode('utf-8')

        create_file(system_context, file_name, to_write, **kwargs)
