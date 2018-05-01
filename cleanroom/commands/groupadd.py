# -*- coding: utf-8 -*-
"""groupadd command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.helper.generic.group as group


class GroupaddCommand(cmd.Command):
    """The groupadd command."""

    def __init__(self):
        """Constructor."""
        super().__init__('groupadd', syntax='<NAME> [force=False] '
                         '[system=False] [gid=<GID>]', help='Add a group.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs exactly one name.',
                                  *args)
        self._validate_kwargs(location, ('force', 'gid', 'system'), **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        group.groupadd(system_context, args[0], **kwargs)
