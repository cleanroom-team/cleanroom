# -*- coding: utf-8 -*-
"""groupmod command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.exceptions import ParseError
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class GroupModCommand(Command):
    """The groupmod command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__('groupmod',
                         syntax='<NAME> [gid=<GID>] [rename=<NEW_NAME>] '
                         '[password=<CRYPTED_PASSWORD>] [root_directory=<CHROOT>]',
                         help_string='Modify an existing user.',
                         file=__file__, **services)

    def validate(self, location: Location,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs a groupname.', *args)
        self._validate_kwargs(location,
                              ('gid', 'rename', 'password', 'root_directory',),
                              **kwargs)
        if len(kwargs) == 0:
            raise ParseError('groupmod needs something to change.',
                             location=location)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        self._service('group_helper').groupmod(args[0], **kwargs,
                                               root_directory=system_context.fs_directory)
