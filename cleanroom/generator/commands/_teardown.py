# -*- coding: utf-8 -*-
"""_teardown command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.generator.command import Command
from cleanroom.generator.context import Binaries

from cleanroom.helper.btrfs import delete_subvolume
from cleanroom.printer import debug


class _TeardownCommand(Command):
    """The _teardown Command."""

    def __init__(self):
        """Constructor."""
        super().__init__('_teardown',
                         help='Implicitly run after any other command of a '
                         'system is run.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        system_context.run_hooks('_teardown')
        system_context.run_hooks('testing')

        system_context.pickle()

        self._store(location, system_context)
        self._clean_temporary_data(system_context)

    def _store(self, location, system_context):
        system_context.execute(location, '_store')

    def _clean_temporary_data(self, system_context):
        """Clean up temporary data."""
        debug('Removing {}.'.format(system_context.current_system_directory()))
        delete_subvolume(system_context.current_system_directory(),
                         command=system_context.binary(Binaries.BTRFS))
