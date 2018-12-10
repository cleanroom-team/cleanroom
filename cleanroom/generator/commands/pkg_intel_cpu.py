"""pkg_intel_cpu command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.file import exists

import os.path


class PkgIntelCpuCommand(Command):
    """The pkg_intel_cpu command."""

    def __init__(self):
        """Constructor."""
        super().__init__('pkg_intel_cpu',
                         help='Install everything for intel CPU.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""

        # Nested virtualization:
        system_context.execute(location, 'create', '/etc/modprobe.d/kvm_intel.conf',
                'options kvm_intel nested=1')

        # Intel ucode:
        location.set_description('Install intel-ucode')
        system_context.execute(location, 'pacman', 'intel-ucode')

        initrd_parts = os.path.join(system_context
                                    .boot_data_directory(),
                                    'initrd-parts')
        os.makedirs(initrd_parts, exist_ok=True)
        system_context.execute(location, 'move', '/boot/intel-ucode.img',
                               os.path.join(initrd_parts, '00-intel-ucode'),
                               to_outside=True)

        # enable kms:
        system_context.execute(location, 'sed',
                               's/^MODULES=(/MODULES=(crc32c-intel /',
                               '/etc/mkinitcpio.conf')

        # Clean out firmware:
        system_context.execute(location, 'remove', '/usr/lib/firmware/amd-ucode/*',
                               force=True)
