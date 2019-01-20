# -*- coding: utf-8 -*-
"""pkg_quasselcore command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command


class PkgQuasselcoreCommand(Command):
    """The pkg_quasselcore command."""

    def __init__(self):
        """Constructor."""
        super().__init__('pkg_quasselcore', help='Setup quasselcore.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        system_context.execute(location.next_line(), 'pacman', 'quassel-core', 'postgresql-libs')
        system_context.execute(location.next_line(), 'systemd_harden_unit', 'quassel.service')
        system_context.execute(location.next_line(), 'systemd_enable', 'quassel.service')
