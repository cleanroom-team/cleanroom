"""pkg_intel_gpu command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import typing


class PkgIntelGpuCommand(Command):
    """The pkg_intel_gpu command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('pkg_intel_gpu',
                         help_string='Set up Intel GPU.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""

        # Enable KMS:
        system_context.execute(location, 'pkg_intel_kms')

        system_context.execute(location, 'pkg_xorg')

        # Set some kernel parameters:
        cmdline = system_context.substitution('KERNEL_CMDLINE', '')
        if cmdline:
            cmdline += ' '
        cmdline += 'intel_iommu=igfx_off i915.fastboot=1'
        system_context.set_substitution('KERNEL_CMDLINE', cmdline)

        system_context.execute(location, 'pacman', 'libva-intel-driver',
                               'mesa', 'vulkan-intel', 'xf86-video-intel')

        system_context.execute(location, 'create', '/etc/modprobe.d/i915-guc.conf',
                               'options i915 enable_guc=3')

        system_context.execute(location, 'remove', '/usr/lib/firmware/amdgpu/*',
                               '/usr/lib/firmware/nvidia/*', '/usr/lib/firmware/radeon/*',
                               force=True, recursive=True)
