# -*- coding: utf-8 -*-
"""systemd_enable command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.helper.generic.systemd as sd


class SystemdEnableCommand(cmd.Command):
    """The systemd_enable command."""

    def __init__(self):
        """Constructor."""
        super().__init__('systemd_enable', syntax='<UNIT> [<MORE_UNITS>]',
                         help='Enable systemd units.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        return self._validate_at_least_arguments(location, 1,
                                                 '"{}" needs at least one '
                                                 'unit to enable.',
                                                 *args, *+kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        sd.systemd_enable(*args)
