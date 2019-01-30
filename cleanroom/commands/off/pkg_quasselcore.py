# -*- coding: utf-8 -*-
"""pkg_quasselcore command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import typing


class PkgQuasselcoreCommand(Command):
    """The pkg_quasselcore command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('pkg_quasselcore', help_string='Setup quasselcore.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        system_context.execute(location.next_line(), 'pacman', 'quassel-core', 'postgresql-libs')
        system_context.execute(location.next_line(), 'systemd_harden_unit', 'quassel.service')
        system_context.execute(location.next_line(), 'systemd_enable', 'quassel.service')

        system_context.execute(location.next_line(), 'net_firewall_open_port', 4242,
                               protocol='tcp', comment='Quassel')
