# -*- coding: utf-8 -*-
"""ensure_no_kernel_install command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class EnsureNoKernelInstallCommand(Command):
    """The ensure_no_kernel_install command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__('ensure_no_kernel_install',
                         help_string='Set up system for a read-only /usr partition.',
                         file=__file__, **services)

    def validate(self, location: Location,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        # Things to update/clean on export:
        location.set_description('Remove kernel-install')
        self._add_hook(location, system_context,
                       'export', 'remove', '/usr/lib/kernel', '/etc/kernel',
                       '/usr/bin/kernel-install', recursive=True, force=True)
