# -*- coding: utf-8 -*-
"""_teardown command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.command as cmd
import cleanroom.helper.generic.btrfs as btrfs
import cleanroom.printer as printer


class _TeardownCommand(cmd.Command):
    """The _teardown Command."""

    def __init__(self):
        """Constructor."""
        super().__init__('_teardown',
                         help='Implicitly run after any other command of a '
                         'system is run.')

    def validate_arguments(self, location, *args, **kwargs):
        return self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        system_context.run_hooks('_teardown')
        system_context.run_hooks('testing')

        system_context.pickle()

        self._store(system_context)
        self._clean_temporary_data(system_context)

    def _store(self, system_context):
        printer.debug('Storing {} into {}.'
                      .format(system_context.ctx.current_system_directory(),
                              system_context.storage_directory()))
        btrfs.create_snapshot(system_context,
                              system_context.ctx.current_system_directory(),
                              system_context.storage_directory(),
                              read_only=True)

    def _clean_temporary_data(self, system_context):
        """Clean up temporary data."""
        printer.debug('Removing {}.'
                      .format(system_context.ctx.current_system_directory()))
        btrfs.delete_subvolume(system_context,
                               system_context.ctx.current_system_directory())
