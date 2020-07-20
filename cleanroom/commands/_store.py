# -*- coding: utf-8 -*-
"""_store command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.command import Command
from cleanroom.systemcontext import SystemContext

import os
import typing


class StoreCommand(Command):
    """The _store command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_store", help_string="Store a system.", file=__file__, **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

        return None

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""

        btrfs_helper = self._service("btrfs_helper")

        btrfs_helper.create_subvolume(system_context.system_storage_directory)

        storage = system_context.system_storage_directory
        btrfs_helper.create_snapshot(
            system_context.meta_directory, os.path.join(storage, "meta"), read_only=True
        )
        btrfs_helper.create_snapshot(
            system_context.boot_directory, os.path.join(storage, "boot"), read_only=True
        )
        btrfs_helper.create_snapshot(
            system_context.fs_directory, os.path.join(storage, "fs"), read_only=True
        )
