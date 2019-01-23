# -*- coding: utf-8 -*-
"""_teardown command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command, ServicesType
from cleanroom.systemcontext import SystemContext
from cleanroom.location import Location
from cleanroom.printer import debug

import typing


class _TeardownCommand(Command):
    """The _teardown Command."""

    def __init__(self, *, services: ServicesType) -> None:
        """Constructor."""
        super().__init__(help_string='Implicitly run after any other command of a '
                         'system is run.', file=__file__,
                         services=services)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> None:
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        system_context.run_hooks('_teardown')
        system_context.run_hooks('testing')

        system_context.pickle()

        self.execute(location, system_context, '_store')
        self._clean_temporary_data(system_context.scratch_directory)

    def _clean_temporary_data(self, scratch_directory: str) -> None:
        """Clean up temporary data."""
        debug('Cleaning up everything in "{}".'.format(scratch_directory))

        self.service('btrfs_helper').delete_subvolume_recursive(scratch_directory)
