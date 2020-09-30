# -*- coding: utf-8 -*-
"""_create_root_fsimage command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.exceptions import GenerateError
from cleanroom.location import Location
from cleanroom.helper.file import size_extend
from cleanroom.helper.run import run
from cleanroom.systemcontext import SystemContext

import typing


class CreateRootFsimageCommand(Command):
    """The _create_root_fsimage Command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        self._root_partition = ""
        self._verity_partition = ""

        self._root_hash = ""

        self._skip_validation = False

        super().__init__(
            "_create_root_fsimage",
            syntax="<ROOTFS_IMAGE> [usr_only=True]",
            help_string="Create a root filesystem image",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate arguments."""
        self._validate_args_exact(
            location, 1, "{} needs a file name for the root filesystem image.", *args
        )
        self._validate_kwargs(location, ("usr_only",), **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        self._usr_only = kwargs.get("usr_only", True)

        rootfs_file = args[0]

        rootfs_label = system_context.substitution_expanded("ROOTFS_PARTLABEL", "")
        if not rootfs_label:
            raise GenerateError("ROOTFS_PARTLABEL is unset.")
        target_directory = "usr" if self._usr_only else "."
        target_args = ["-keep-as-directory"] if self._usr_only else []
        run(
            self._binary(Binaries.MKSQUASHFS),
            target_directory,
            rootfs_file,
            *target_args,
            "-comp",
            "gzip",  # compression does not matter: We disable compression!
            "-noappend",
            "-no-exports",
            "-noI",
            "-noD",
            "-noF",
            "-noX",
            "-processors",
            "1",
            work_directory=system_context.fs_directory
        )
        size_extend(rootfs_file)
