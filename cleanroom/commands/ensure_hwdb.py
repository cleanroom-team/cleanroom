# -*- coding: utf-8 -*-
"""ensure_hwdb command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import os
import typing


class EnsureHwdbCommand(Command):
    """The ensure_hwdb command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('ensure_hwdb',
                         help_string='Make sure hwdb is installed.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        assert os.path.exists(system_context.file_name('/usr/bin/systemd-hwdb'))

        location.set_description('Update HWDB')
        system_context.add_hook(location, 'export', 'run',
                                '/usr/bin/systemd-hwdb', '--usr', 'update')
        location.set_description('Remove HWDB data')
        system_context.add_hook(location, 'export', 'remove',
                                '/usr/bin/systemd-hwdb')
        location.set_description('Remove HWDB related services')
        system_context.add_hook(location, 'export', 'remove',
                                '/usr/lib/systemd/system/*/'
                                'systemd-hwdb-update.service',
                                '/usr/lib/systemd/system/'
                                'systemd-hwdb-update.service', force=True)
