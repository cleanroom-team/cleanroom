# -*- coding: utf-8 -*-
"""symlink command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.helper.file import symlink
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class SymlinkCommand(Command):
    """The symlink command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__('symlink',
                         syntax='<SOURCE> <TARGET> [work_directory=BASE]',
                         help_string='Create a symlink.', file=__file__,
                         **services)

    def validate(self, location: Location,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Validate the arguments."""
        self._validate_args_exact(location, 2,
                                  '"{}" needs a source and a target.', *args)
        self._validate_kwargs(location, ('work_directory',), **kwargs)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        symlink(system_context, args[0], args[1],
                work_directory=kwargs.get('work_directory', None))
