# -*- coding: utf-8 -*-
"""chown command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.file import chown


class ChownCommand(Command):
    """The chown command."""

    def __init__(self):
        """Constructor."""
        super().__init__('chown', syntax='<FILE>+ [user=<USER>] [group=<GROUP>] '
                         '[recursive=False]',
                         help='Chmod a file or files.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_at_least(location, 1,
                                     '"{}" takes one or more files.', *args)
        self._validate_kwargs(location, ('user', 'group', 'recursive',), **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        user = kwargs.get('user', 'root')
        group = kwargs.get('group', 'root')
        chown(system_context, user, group, *args,
              recursive=kwargs.get('recursive', False))
