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
        self._validate_installation(run_context,
                                    file_name=file_name,
                                    line_number=line_number)
        self._run_hooks(run_context)

        self._export(run_context)

    def _validate_installation(self, run_context, *,
                               file_name='', line_number=-1):
        hostname = run_context.substitution('HOSTNAME')
        if hostname is None:
            raise ex.GenerateError('Trying to export a system without '
                                   'a hostname.',
                                   file_name=file_name,
                                   line_number=line_number)
        machine_id = run_context.substitution('MACHINE_ID')
        if machine_id is None:
            raise ex.GenerateError('Trying to export a system without '
                                   'a machine_id.',
                                   file_name=file_name,
                                   line_number=line_number)

    def _run_hooks(self, run_context):
        run_context.run_hooks('_teardown')
        run_context.run_hooks('export')

        # Now do tests!
        run_context.run_hooks('testing')

    def _export(self, run_context):
        repository = run_context.ctx.export_repository()
        if repository == '':
            return

        borg = run_context.ctx.binary(context.Binaries.BORG)
        backup_name = run_context.system + '-' + run_context.timestamp

        run_context.run(borg, 'create', '--compression', 'zstd,22',
                        '--numeric-owner', '--noatime',
                        '{}::{}'.format(repository, backup_name),
                        run_context.current_system_directory(),
                        outside=True)
