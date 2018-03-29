# -*- coding: utf-8 -*-
"""pacman command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.helper.archlinux.pacman as arch


class PacmanCommand(cmd.Command):
    """The pacman command."""

    def __init__(self):
        """Constructor."""
        super().__init__('pacman', syntax='<PACKAGES>',
                         help='Run pacman to install <PACKAGES>.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        return self._validate_arguments_at_least(location, 1,
                                                '"{}"" needs at least '
                                                'one package or group to '
                                                'install.', *args, **kwargs)
        return None

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        arch.pacman(system_context, *args)
