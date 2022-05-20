"""pkg_intel_gpu command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class PkgIntelGpuCommand(Command):
    """The pkg_intel_gpu command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "pkg_intel_gpu", help_string="Set up Intel GPU.", file=__file__, **services
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

        # Enable KMS:
        self._execute(location, system_context, "pkg_intel_kms")

        self._execute(location, system_context, "pkg_xorg")

        # Set some kernel parameters:
        system_context.set_or_append_substitution(
            "KERNEL_CMDLINE", "i915.fastboot=1 intel_iommu=igfx_off"
        )

        self._execute(
            location,
            system_context,
            "pacman",
            "libva-intel-driver",
            "mesa",
            "vulkan-intel",
            "xf86-video-intel",
            "intel-media-driver",
        )

        self._execute(
            location.next_line(),
            system_context,
            "create",
            "/etc/modprobe.d/i915-guc.conf",
            "options i915 enable_guc=3",
        )

        self._execute(
            location.next_line(),
            system_context,
            "remove",
            "/usr/lib/firmware/amdgpu/*",
            "/usr/lib/firmware/nvidia/*",
            "/usr/lib/firmware/radeon/*",
            force=True,
            recursive=True,
        )
