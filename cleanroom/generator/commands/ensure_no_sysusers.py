# -*- coding: utf-8 -*-
"""ensure_no_sysusers command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command


class EnsureNoSysusersCommand(Command):
    """The ensure_no_sysusers command."""

    def __init__(self):
        """Constructor."""
        super().__init__('ensure_no_sysusers',
                         help='Set up system for a read-only /usr partition.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        # Things to update/clean on export:
        location.set_description('Remove systemd-sysusers')
        system_context.add_hook(location, 'export', 'remove',
                                '/usr/lib/sysusers.d', '/usr/bin/systemd-sysusers',
                                recursive=True, force=True)

