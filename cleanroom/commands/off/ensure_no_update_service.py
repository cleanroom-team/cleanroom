# -*- coding: utf-8 -*-
"""ensure_no_update_service command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import typing


class EnsureNoUpdateServiceCommand(Command):
    """The ensure_no_update_service command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('ensure_no_update_service',
                         help_string='Set up system for a read-only /usr partition.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        # Remove unnecessary systemd-services:
        system_context.execute(location.next_line(), 'remove',
                               '/usr/lib/systemd/system/systemd-update-done.service',
                               '/usr/lib/systemd/system/'
                               'system-update-cleanup.service',
                               '/usr/lib/systemd/system/system-update.target',
                               '/usr/lib/systemd/system/system-update-pre.target',
                               '/usr/lib/systemd/system-generators/'
                               'systemd-system-update-generator',
                               '/usr/lib/systemd/systemd-update-done',
                               force=True)
