# -*- coding: utf-8 -*-
"""normalize_kernel_install command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
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
        for kernel in ('linux', 'linux-hardened', 'linux-lts', 'linux-zen', 'linux-git',):
            self._execute(location, system_context,
                          'move', '/etc/mkinitcpio.d/{}.preset'.format(kernel),
                          '/etc/mkinitcpio.d/cleanroom.preset',
                          ignore_missing_sources=True, force=True)

            self._execute(location.next_line(), system_context,
                          'move', '/boot/vmlinuz-{}'.format(kernel),
                          '/boot/vmlinuz',
                          ignore_missing_sources=True, force=True)

        self._execute(location.next_line(), system_context,
                      'copy', '/boot/vmlinuz',
                      os.path.join(system_context.boot_directory, 'vmlinuz'),
                      to_outside=True)
