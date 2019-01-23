# -*- coding: utf-8 -*-
"""ensure_ldconfig command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import os
import typing


class EnsureLdconfigCommand(Command):
    """The ensure_ldconfig command."""

    def __init__(self):
        """Constructor."""
        super().__init__('ensure_ldconfig',
                         help_string='Ensure that ldconfig is run.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        assert os.path.exists(system_context.file_name('/usr/bin/ldconfig'))

        location.set_description('Run ldconfig')
        system_context.add_hook(location, 'export', 'run', '/usr/bin/ldconfig', '-X')
        location.set_description('Remove ldconfig data')
        system_context.add_hook(location, 'export', 'remove', '/usr/bin/ldconfig')
        location.set_description('Remove ldconfig related services')
        system_context.add_hook(location, 'export', 'remove',
                                '/usr/lib/systemd/system/*/ldconfig.service',
                                '/usr/lib/systemd/system/ldconfig.service',
                                force=True)
