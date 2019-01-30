# -*- coding: utf-8 -*-
"""groupadd command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.group import groupadd
from cleanroom.generator.systemcontext import SystemContext

import typing


class GroupaddCommand(Command):
    """The groupadd command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('groupadd', syntax='<NAME> [force=False] '
                         '[system=False] [gid=<GID>]', help_string='Add a group.',
                         file=__file__)

    def validate_arguments(self, location: Location,
                           *args: typing.Any, **kwargs: typing.Any) -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs exactly one name.',
                                  *args)
        self._validate_kwargs(location, ('force', 'gid', 'system'), **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        groupadd(system_context, args[0], **kwargs)
