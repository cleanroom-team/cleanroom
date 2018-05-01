# -*- coding: utf-8 -*-
"""_export_directory command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.context as context


class ExportDirectoryCommand(cmd.Command):
    """The _export_directory command."""

    def __init__(self):
        """Constructor."""
        super().__init__('_export_directory', syntax='<DIRECTORY>',
                         help='Export a directory from cleanroom.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_arguments_exact(location, 1, '"{}" needs a directory '
                                       'to export_directory.', *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        export_directory = args[0]
        repository = system_context.ctx.export_repository()
        if repository == '':
            return

        borg = system_context.ctx.binary(context.Binaries.BORG)
        backup_name = system_context.system + '-' + system_context.timestamp

        system_context.run(borg, 'create', '--compression', 'zstd,22',
                           '--numeric-owner', '--noatime',
                           '{}::{}'.format(repository, backup_name),
                           export_directory, outside=True)
