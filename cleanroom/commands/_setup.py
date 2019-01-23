# -*- coding: utf-8 -*-
"""_setup command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command, ServicesType
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class _SetupCommand(Command):
    """The _setup Command."""

    def __init__(self, *, services: ServicesType) -> None:
        """Constructor."""
        super().__init__(help_string='Implicitly run before any '
                         'other command of a system is run.',
                         file=__file__,
                         services=services)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        pass
