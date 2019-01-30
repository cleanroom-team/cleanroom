# -*- coding: utf-8 -*-
"""groupmod command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.exceptions import ParseError
from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.group import groupmod
from cleanroom.generator.systemcontext import SystemContext

import typing


class GroupModCommand(Command):
    """The groupmod command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('groupmod',
                         syntax='<NAME> [gid=<GID>] [rename=<NEW_NAME>] '
                         '[password=<CRYPTED_PASSWORD>] [root_directory=<CHROOT>]',
                         help_string='Modify an existing user.', file=__file__)

    def validate_arguments(self, location: Location,
                           *args: typing.Any, **kwargs: typing.Any) -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs a groupname.', *args)
        self._validate_kwargs(location,
                              ('gid', 'rename', 'password', 'root_directory',),
                              **kwargs)
        if len(kwargs) == 0:
            raise ParseError('groupmod needs something to change.',
                             location=location)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        groupmod(system_context, args[0], **kwargs)
