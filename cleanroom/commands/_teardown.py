"""_teardown command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.command as cmd
import cleanroom.helper.generic.btrfs as btrfs


class _TeardownCommand(cmd.Command):
    """The _teardown Command."""

    def __init__(self):
        """Constructor."""
        super().__init__("_teardown",
                         "Implicitly run after any other command of a "
                         "system is run.")

    def validate_arguments(self, run_context, *args, **kwargs):
        return self._validate_no_arguments(run_context, *args, **kwargs)

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        run_context.run_hooks('_teardown')
        run_context.run_hooks('testing')

        run_context.pickle()

        self._store(run_context)
        self._clean_temporary_data(run_context)

    def _store(self, run_context):
        run_context.ctx.printer.debug(
            'Storing {} into {}.'
            .format(run_context.current_system_directory(),
                    run_context.storage_directory()))
        btrfs.create_snapshot(run_context,
                              run_context.current_system_directory(),
                              run_context.storage_directory(), read_only=True)

    def _clean_temporary_data(self, run_context):
        """Clean up temporary data."""
        run_context.ctx.printer.debug(
            'Removing {}.'
            .format(run_context.current_system_directory()))
        btrfs.delete_subvolume(run_context,
                               run_context.current_system_directory())
