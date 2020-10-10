"""pkg_amd_cpu command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.helper.file import create_file
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os
import typing


class PkgAmdCpuCommand(Command):
    """The pkg_amd_cpu command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "pkg_amd_cpu",
            help_string="Install everything for amd CPU.",
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

        # Nested virtualization:
        create_file(
            system_context,
            "/etc/modprobe.d/kvm_amd.conf",
            "options kvm_amd nested=1".encode("utf-8"),
        )

        # AMD ucode:
        location.set_description("Install amd-ucode")
        self._execute(location, system_context, "pacman", "amd-ucode")

        os.makedirs(system_context.initrd_parts_directory, exist_ok=True)
        self._execute(
            location,
            system_context,
            "move",
            "/boot/amd-ucode.img",
            os.path.join(system_context.initrd_parts_directory, "00-amd-ucode"),
            to_outside=True,
        )
