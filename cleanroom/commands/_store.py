# -*- coding: utf-8 -*-
"""_store command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.command import Command, ServicesType
from cleanroom.systemcontext import SystemContext
from cleanroom.printer import debug

import typing


class _StoreCommand(Command):
    """The _store command."""

    def __init__(self, *, services: ServicesType) -> None:
        """Constructor."""
        super().__init__(help_string='Store a system.',
                         file=__file__,
                         services=services)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        assert system_context.ctx
        debug('Storing {} into {}.'.format(system_context.current_system_directory,
                                           system_context.storage_directory))
        store_work_directory(system_context.ctx,
                             system_context.current_system_directory,
                             system_context.storage_directory)
