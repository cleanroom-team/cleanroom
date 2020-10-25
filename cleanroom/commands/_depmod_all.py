# -*- coding: utf-8 -*-
"""_depmod_all command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os
import typing


class DepmodAllCommand(Command):
    """The depmod_all command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_depmod_all",
            help_string="Make sure all module dependecies are up to date.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        modules = system_context.file_name("/usr/lib/modules")
        if not os.path.isdir(modules):
            return  # No kernel installed, nothing to do.

        kernel_version = system_context.substitution_expanded("KERNEL_VERSION", "")
        assert kernel_version

        location.set_description(f"Run depmod for kernel version {kernel_version}...")
        self._execute(
            location,
            system_context,
            "run",
            self._binary(Binaries.DEPMOD),
            "-a",
            "-b",
            system_context.fs_directory,
            kernel_version,
        )
