# -*- coding: utf-8 -*-
"""pkg_tmux command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import typing


class PkgTmuxCommand(Command):
    """The pkg_tmux command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('pkg_tmux', help_string='Setup tmux.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        system_context.execute(location.next_line(),
                               'pacman', 'tmux')

        system_context.execute(location.next_line(),
                               'create', '/root/.tmux.conf',
                               '''# Set activation key to ctrl-A:
set-option -g prefix C-a

# Rebind splitting to | and -:
unbind %
bind | split-window -h
bind - split-window -v

# Last window on C-a C-a:
bind-key C-a last-window

# Highlight active window
set-window-option -g window-status-current-bg red

# Set window notifications
setw -g monitor-activity on
set -g visual-activity on
''',
                               mode=0o600)
