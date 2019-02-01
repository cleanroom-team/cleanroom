# -*- coding: utf-8 -*-
"""_setup command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.binarymanager import BinaryManager, Binaries
from cleanroom.command import Command
from cleanroom.helper.btrfs import BtrfsHelper
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os
import typing


def _setup_scratch_directory(system_context: SystemContext,
                             btrfs_helper: BtrfsHelper) -> None:
    btrfs_helper.create_subvolume(system_context.fs_directory)
    btrfs_helper.create_subvolume(system_context.cache_directory)
    btrfs_helper.create_subvolume(system_context.meta_directory)
    btrfs_helper.create_subvolume(system_context.boot_directory)


def _setup_fs_directory(system_context: SystemContext,
                        mknod_command: str) -> None:
    # Make sure systemd does not create /var/lib/* for us!
    os.makedirs(system_context.file_name('var/lib/machines'))
    os.makedirs(system_context.file_name('var/lib/portables'))

    # Make sure there is /dev/null in the filesystem:
    os.makedirs(system_context.file_name('dev'))

    run(mknod_command, '--mode=666',
        system_context.file_name('dev/null'), 'c', '1', '3')
    run(mknod_command, '--mode=666',
        system_context.file_name('dev/zero'), 'c', '1', '5')
    run(mknod_command, '--mode=666',
        system_context.file_name('dev/random'), 'c', '1', '8')


class _SetupCommand(Command):
    """The _setup Command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__('_setup',
                         help_string='Implicitly run before any '
                                     'other command of a system is run.',
                         file=__file__, **services)

    def validate(self, location: Location,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        _setup_scratch_directory(system_context,
                                 self._service('btrfs_helper'))
        _setup_fs_directory(system_context, self._binary(Binaries.MKNOD))
