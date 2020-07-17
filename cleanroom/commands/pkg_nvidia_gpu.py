"""pkg_nvidia_gpu command.

@author: Paul Hunnisett <phunnilemur@gmail.com>
"""

from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class PkgNvidiaGpuCommand(Command):
    """The pkg_nvidia_gpu command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "pkg_nvidia_gpu",
            help_string="Set up NVidia GPU.",
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

        # Set some kernel parameters for:
        system_context.set_or_append_substitution(
            "KERNEL_CMDLINE", "nvidia-drm.modeset=1 nouveau.blacklist=1"
        )

        self._execute(
            location,
            system_context,
            "pacman",
            "nvidia",
            "nvidia-settings",
            "nvidia-utils",
            "opencl-nvidia",
            "libvdpau",
            "lib32-libvdpau",
            "lib32-nvidia-utils",
            "lib32-opencl-nvidia",
            "vdpauinfo",
            "mesa",
            "mesa-demos",
        )

        self._execute(
            location.next_line(),
            system_context,
            "create",
            "/etc/modprobe.d/nouveau-blacklist.conf",
            "blacklist nouveau",
        )
