# -*- coding: utf-8 -*-
"""ensure_no_sysusers command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class EnsureNoSysusersCommand(Command):
    """The ensure_no_sysusers command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__('ensure_no_sysusers',
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
        location.set_description('Remove systemd-sysusers')
        self._add_hook(location, system_context,
                       'export', 'remove', '/usr/lib/sysusers.d',
                       '/usr/bin/systemd-sysusers',
                       '/usr/lib/systemd/system/sysinit.target.wants/'
                       'systemd-sysusers.service',
                       '/usr/lib/systemd/system/systemd-sysusers.service',
                       recursive=True, force=True)
