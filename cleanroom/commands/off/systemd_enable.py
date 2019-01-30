# -*- coding: utf-8 -*-
"""systemd_enable command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.systemd import systemd_enable
from cleanroom.generator.systemcontext import SystemContext

import typing


class SystemdEnableCommand(Command):
    """The systemd_enable command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('systemd_enable',
                         syntax='<UNIT> [<MORE_UNITS>] [user=False]',
                         help_string='Enable systemd units.', file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_args_at_least(location, 1,
                                     '"{}" needs at least one '
                                     'unit to enable.', *args)
        self._validate_kwargs(location, ('user',), **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        systemd_enable(system_context, *args, **kwargs)
