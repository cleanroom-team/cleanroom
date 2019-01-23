# -*- coding: utf-8 -*-
"""export_rootfs command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.exceptions import ParseError
from cleanroom.location import Location
from cleanroom.generator.context import Binaries
from cleanroom.generator.exportcommand import ExportCommand
from cleanroom.generator.systemcontext import SystemContext
from cleanroom.helper.btrfs import create_snapshot, create_subvolume, \
    delete_subvolume, delete_subvolume_recursive

import os.path
import typing


class ExportRootFsCommand(ExportCommand):
    """The export_rootfs Command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('export_rootfs',
                         syntax='[tarballs={dir: name, dir2: name2}]',
                         help='Export the root filesystem.',
                         file=__file__)
        self._tarballs = ''
        self._export_volume = ''

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate arguments."""
        self._validate_no_args(location, *args)
        self._validate_kwargs(location, ('tarballs',), **kwargs)

        return None

    def set_arguments_and_kwargs(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        self._tarballs = kwargs.get('tarballs', '')

    def _create_tarballs(self, location: Location, system_context: SystemContext,
                         directory: str, tarball: str) -> None:
        system_context.run('tar', '-cf',
                           os.path.join(self._export_volume, tarball) + '.tar', '.',
                           outside=True)
        to_remove = directory
        if not os.path.isabs(to_remove):
            to_remove = system_context.file_name('/' + to_remove) + '/*'
        system_context.execute(location, 'remove', to_remove,
                               recursive=True, force=True)

    def create_export_directory(self, location: Location, system_context: SystemContext) \
            -> str:
        """Return the root directory."""
        assert system_context.ctx
        work_directory = system_context.ctx.work_directory()
        assert work_directory
        self._export_volume = os.path.join(work_directory, 'export')
        if os.path.isdir(self._export_volume):
            delete_subvolume_recursive(self._export_volume, 
                                       command=system_context.binary(Binaries.BTRFS))
        
        create_subvolume(self._export_volume,
                         command=system_context.binary(Binaries.BTRFS))
        
        for tb in self._tarballs.split(','):
            if not tb:
                continue

            (directory, tarball) = tb.split(':')
            if not tarball:
                raise ParseError('No tarball name given.', location)
            self._create_tarballs(location, system_context,
                                  directory, tarball)

        create_snapshot(system_context.fs_directory(),
                        os.path.join(self._export_volume, 'fs'),
                        command=system_context.binary(Binaries.BTRFS))

        return self._export_volume

    def delete_export_directory(self, system_context: SystemContext, export_directory: str) -> None:
        """Nothing to see, move on."""
        delete_subvolume(os.path.join(export_directory, 'fs'),
                         command=system_context.binary(Binaries.BTRFS))
        delete_subvolume(export_directory,
                         command=system_context.binary(Binaries.BTRFS))

        self._export_volume = ''
