"""_teardown command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.command as cmd
import cleanroom.context as context
import cleanroom.run as run


class _TeardownCommand(cmd.Command):
    """The _teardown Command."""

    def __init__(self):
        """Constructor."""
        super().__init__("_teardown",
                         "Implicitly run after any other command of a "
                         "system is run.")

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        run_context.run_hooks('_teardown')

        run_context.pickle()

        self.store_to_ostree(run_context)

    def store_to_ostree(self, run_context):
        run_context.ctx.printer.debug('Storing results in ostree.')
        ostree = run_context.ctx.binary(context.Binaries.OSTREE)

        run.run(ostree,
                'commit',
                '--repo={}'
                .format(run_context.ctx.work_repository_directory()),
                '--branch', run_context.system,
                '--subject', run_context.timestamp,
                '--add-metadata-string="timestamp={}"'
                .format(run_context.timestamp),
                work_directory=run_context.system_directory(),
                trace_output=run_context.ctx.printer.trace)
