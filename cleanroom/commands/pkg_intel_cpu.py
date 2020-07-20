"""pkg_intel_cpu command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os
import typing


class PkgIntelCpuCommand(Command):
    """The pkg_intel_cpu command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "pkg_intel_cpu",
            help_string="Install everything for intel CPU.",
            file=__file__,
            **services
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
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""

        # Nested virtualization:
        self._execute(
            location,
            system_context,
            "create",
            "/etc/modprobe.d/kvm_intel.conf",
            "options kvm_intel nested=1",
        )

        # Intel ucode:
        location.set_description("Install intel-ucode")
        self._execute(location, system_context, "pacman", "intel-ucode")

        initrd_parts = os.path.join(system_context.boot_directory, "initrd-parts")
        os.makedirs(initrd_parts, exist_ok=True)
        self._execute(
            location,
            system_context,
            "move",
            "/boot/intel-ucode.img",
            os.path.join(initrd_parts, "00-intel-ucode"),
            to_outside=True,
        )

        system_context.set_or_append_substitution(
            "MKINITCPIO_EXTRA_MODULES", "crc32c-intel"
        )

        # Clean out firmware:
        self._execute(
            location.next_line(),
            system_context,
            "remove",
            "/usr/lib/firmware/amd-ucode/*",
            force=True,
        )
