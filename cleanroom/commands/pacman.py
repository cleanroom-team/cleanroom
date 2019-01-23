# -*- coding: utf-8 -*-
"""pacman command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.helper.archlinux.pacman import pacman
from cleanroom.generator.systemcontext import SystemContext

import typing


class PacmanCommand(Command):
    """The pacman command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('pacman', syntax='<PACKAGES> [remove=False] '
                         '[overwrite=GLOB] [assume_installed=PKG]',
                         help_string='Run pacman to install <PACKAGES>.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_args_at_least(location, 1, '"{}"" needs at least '
                                     'one package or group to install.', *args)
        self._validate_kwargs(location, ('remove', 'overwrite',
                                         'assume_installed',), **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        pacman(system_context, *args, **kwargs)
