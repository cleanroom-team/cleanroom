# -*- coding: utf-8 -*-
"""_export_directory command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.context import Binaries


class ExportDirectoryCommand(Command):
    """The _export_directory command."""

    def __init__(self):
        """Constructor."""
        super().__init__('_export_directory', syntax='<DIRECTORY> compression_level=<X>',
                         help='Export a directory from cleanroom.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs a directory '
                                  'to export.', *args)
        self._validate_kwargs(location, ('compression_level',), **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        export_directory = args[0]
        repository = system_context.ctx.repository()
        if repository == '':
            return

        borg = system_context.binary(Binaries.BORG)
        backup_name = system_context.system + '-' + system_context.timestamp

        system_context.run(borg, 'create', '--compression',
                           'zstd,{}'.format(kwargs.get('compression_level', 4)),
                           '--numeric-owner', '--noatime',
                           '{}::{}'.format(repository, backup_name),
                           '.', outside=True, work_directory=export_directory)
