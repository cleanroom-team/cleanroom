# -*- coding: utf-8 -*-
"""systemd_enable command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.systemd import systemd_enable


class SystemdEnableCommand(Command):
    """The systemd_enable command."""

    def __init__(self):
        """Constructor."""
        super().__init__('systemd_enable', syntax='<UNIT> [<MORE_UNITS>]',
                         help='Enable systemd units.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_arguments_at_least(location, 1,
                                          '"{}" needs at least one '
                                          'unit to enable.', *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        systemd_enable(system_context, *args)
