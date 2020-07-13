# -*- coding: utf-8 -*-
"""_restore command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os
import typing


class RestoreCommand(Command):
    """The _restore command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_restore",
            syntax="<STATIC> [pretty=<PRETTY>]",
            help_string="Set the hostname of the system.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_arguments_exact(
            location, 1, '"{}" needs a base system to restore.', *args, **kwargs
        )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""

        base = args[0]
        assert (
            system_context.base_context
            and system_context.base_context.system_name == base
        )

        btrfs_helper = self._service("btrfs_helper")

        if not os.path.isdir(system_context.scratch_directory):
            btrfs_helper.create_subvolume(system_context.scratch_directory)
            btrfs_helper.set_property(
                system_context.scratch_directory, name="compression", value="none"
            )

        btrfs_helper.create_snapshot(
            os.path.join(system_context.base_storage_directory, "meta"),
            system_context.meta_directory,
        )
        btrfs_helper.create_snapshot(
            os.path.join(system_context.base_storage_directory, "boot"),
            system_context.boot_directory,
        )
        btrfs_helper.create_snapshot(
            os.path.join(system_context.base_storage_directory, "fs"),
            system_context.fs_directory,
        )

        btrfs_helper.create_subvolume(system_context.cache_directory)
