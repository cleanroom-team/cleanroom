# -*- coding: utf-8 -*-
"""pkg_tmux command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command


class PkgTmuxCommand(Command):
    """The pkg_tmux command."""

    def __init__(self):
        """Constructor."""
        super().__init__('pkg_tmux', help='Setup tmux.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
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
