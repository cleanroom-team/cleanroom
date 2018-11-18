"""pkg_amd_cpu command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.file import exists

import os.path


class PkgAmdCpuCommand(Command):
    """The pkg_amd_cpu command."""

    def __init__(self):
        """Constructor."""
        super().__init__('pkg_amd_cpu',
                         help='Install everything for amd CPU.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
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

