# -*- coding: utf-8 -*-
"""normalize_kernel_install command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command

import os.path


class NormalizeKernelInstallCommand(Command):
    """The normalize_kernel_install command."""

    def __init__(self):
        """Constructor."""
        super().__init__('normalize_kernel_install',
                         help='Handle different kernel flavors in Arch.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        location.next_line_offset('Handle different kernel flavors')
        system_context.execute(location, 'move',
                               '/etc/mkinitcpio.d/linux-hardened.preset',
                               '/etc/mkinitcpio.d/linux.preset',
                               ignore_missing_sources=True)
        system_context.execute(location, 'move',
                               '/etc/mkinitcpio.d/linux-lts.preset',
                               '/etc/mkinitcpio.d/linux.preset',
                               ignore_missing_sources=True)
        system_context.execute(location, 'move',
                               '/etc/mkinitcpio.d/linux-git.preset',
                               '/etc/mkinitcpio.d/linux.preset',
                               ignore_missing_sources=True)

        system_context.execute(location, 'move','/boot/vmlinuz-linux*',
                               '/boot/vmlinuz')
        system_context.execute(location, 'copy','/boot/vmlinuz',
                               os.path.join(system_context.boot_data_directory(), 'vmlinuz'),
                               to_outside=True)
