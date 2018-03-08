"""export command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.command as cmd
import cleanroom.context as context
import cleanroom.exceptions as ex


class ExportCommand(cmd.Command):
    """The export Command."""

    def __init__(self):
        """Constructor."""
        super().__init__('export',
                         'Export a system and make it available '
                         'for deployment.')

    def __call__(self, file_name, line_number, run_context, *args, **kwargs):
        """Execute command."""
        hostname = run_context.substitution('HOSTNAME')
        if hostname is None:
            raise ex.GenerateError('Trying to export a system without '
                                   'a hostname.',
                                   file_name=file_name,
                                   line_number=line_number)

        self._run_hooks(run_context)

        ostree = run_context.ctx.binary(context.Binaries.OSTREE)
        export_repository = run_context.ctx.export_repository
        filesystem = run_context.fs_directory()

        run_context.run(ostree, 'commit',
                        '--repo={}'.format(export_repository),
                        '--subject={}'.format(hostname),
                        '--branch={}'.format(hostname),
                        '.',
                        work_directory=filesystem,
                        outside=True)

    def _run_hooks(self, run_context):
        run_context.run_hooks('_teardown')
        run_context.run_hooks('export')

        # Now do tests!
        run_context.run_hooks('testing')
