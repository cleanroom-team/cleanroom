# -*- coding: utf-8 -*-
"""normalize_kernel_install command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import os.path
import typing


class NormalizeKernelInstallCommand(Command):
    """The normalize_kernel_install command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('normalize_kernel_install',
                         help_string='Handle different kernel flavors in Arch.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        location.set_description('Handle different kernel flavors')
        for kernel in ('linux', 'linux-hardened', 'linux-lts', 'linux-zen', 'linux-git',):
            system_context.execute(location, 'move',
                                   '/etc/mkinitcpio.d/{}.preset'.format(kernel),
                                   '/etc/mkinitcpio.d/cleanroom.preset',
                                   ignore_missing_sources=True, force=True)

            system_context.execute(location.next_line(), 'move',
                                   '/boot/vmlinuz-{}'.format(kernel),
                                   '/boot/vmlinuz',
                                   ignore_missing_sources=True, force=True)

        system_context.execute(location.next_line(), 'copy', '/boot/vmlinuz',
                               os.path.join(system_context.boot_data_directory(), 'vmlinuz'),
                               to_outside=True)
