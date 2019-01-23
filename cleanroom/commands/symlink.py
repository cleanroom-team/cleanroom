# -*- coding: utf-8 -*-
"""symlink command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext
from cleanroom.generator.helper.generic.file import symlink

import typing


class SymlinkCommand(Command):
    """The symlink command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('symlink',
                         syntax='<SOURCE> <TARGET> [work_directory=BASE]',
                         help_string='Create a symlink.', file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_args_exact(location, 2,
                                  '"{}" needs a source and a target.', *args)
        self._validate_kwargs(location, ('work_directory',), **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        source = args[0]
        target = args[1]
        base = kwargs.get('work_directory', None)

        symlink(system_context, source, target, work_directory=base)
