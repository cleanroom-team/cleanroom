# -*- coding: utf-8 -*-
"""chown command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.file import chown
from cleanroom.generator.systemcontext import SystemContext

import typing


class ChownCommand(Command):
    """The chown command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('chown', syntax='<FILE>+ [user=<USER>] [group=<GROUP>] '
                         '[recursive=False]',
                         help_string='Chmod a file or files.', file=__file__)

    def validate_arguments(self, location: Location,
                           *args: typing.Any, **kwargs: typing.Any) -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_args_at_least(location, 1,
                                     '"{}" takes one or more files.', *args)
        self._validate_kwargs(location, ('user', 'group', 'recursive',), **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        user = kwargs.get('user', 'root')
        group = kwargs.get('group', 'root')
        chown(system_context, user, group, *args,
              recursive=kwargs.get('recursive', False))
