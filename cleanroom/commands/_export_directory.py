# -*- coding: utf-8 -*-
"""_export_directory command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.context import Binaries
from cleanroom.generator.systemcontext import SystemContext

import typing


class ExportDirectoryCommand(Command):
    """The _export_directory command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('_export_directory', syntax='<DIRECTORY> compression_level=<X>',
                         help_string='Export a directory from cleanroom.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs a directory '
                                  'to export.', *args)
        self._validate_kwargs(location, ('compression_level',), **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        export_directory = args[0]
        assert system_context.timestamp

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
