# -*- coding: utf-8 -*-
"""groupadd command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class GroupaddCommand(Command):
    """The groupadd command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__('groupadd', syntax='<NAME> [force=False] '
                         '[system=False] [gid=<GID>]', help_string='Add a group.',
                         file=__file__, **services)

    def validate(self, location: Location,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs exactly one name.',
                                  *args)
        self._validate_kwargs(location, ('force', 'gid', 'system'), **kwargs)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        self._service('group_helper').groupadd(args[0], **kwargs,
                                               root_directory=system_context.fs_directory)
