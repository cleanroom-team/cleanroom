# -*- coding: utf-8 -*-
"""normalize_kernel_install command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.helper.file import makedirs, remove
from cleanroom.systemcontext import SystemContext

import os.path
import typing


class NormalizeKernelInstallCommand(Command):
    """The normalize_kernel_install command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__('normalize_kernel_install',
                         help_string='Handle different kernel flavors in Arch.',
                         file=__file__, **services)

    def validate(self, location: Location,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        location.set_description('Handle different kernel flavors')
        vmlinuz = os.path.join(system_context.boot_directory, 'vmlinuz')
        preset = system_context.file_name('/etc/mkinitcpio.d/cleanroom.preset')

        makedirs(system_context, '/etc/mkinitcpio.d', exist_ok=True)

        # Clean up after the mkinitcpio hook:
        for kernel in ('', '-hardened', '-lts', '-zen', '-git',):
            remove('/boot/vmlinuz{}'.format(kernel), force=True)

            kernel_preset = '/etc/mkinitcpio.d/linux'
            if kernel:
                kernel_preset += '-{}'
            kernel_preset += '.preset'
            remove(kernel_preset, force=True)

        # New style linux packages that put vmlinuz into /usr/lib/modules:
        self._execute(location.next_line(), system_context,
                      'move', '/usr/lib/modules/*/vmlinuz', vmlinuz,
                      to_outside=True, ignore_missing_sources=True)

        if not os.path.isfile(preset):
            self._execute(location.next_line(), system_context,
                          'copy', '/usr/share/mkinitcpio/hook.preset',
                          preset, to_outside=True)

        assert(os.path.isfile(preset))
        assert(os.path.isfile(vmlinuz))
