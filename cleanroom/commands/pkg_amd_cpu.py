"""pkg_amd_cpu command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import os.path
import typing


class PkgAmdCpuCommand(Command):
    """The pkg_amd_cpu command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('pkg_amd_cpu',
                         help_string='Install everything for amd CPU.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""

        # Nested virtualization:
        system_context.execute(location, 'create', '/etc/modprobe.d/kvm_amd.conf',
                               'options kvm_amd nested=1')

        # AMD ucode:
        location.set_description('Install amd-ucode')
        system_context.execute(location, 'pacman', 'amd-ucode')

        initrd_parts = os.path.join(system_context
                                    .boot_data_directory(),
                                    'initrd-parts')
        os.makedirs(initrd_parts, exist_ok=True)
        system_context.execute(location, 'move', '/boot/amd-ucode.img',
                               os.path.join(initrd_parts, '00-amd-ucode'),
                               to_outside=True)
