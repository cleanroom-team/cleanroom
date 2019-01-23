# -*- coding: utf-8 -*-
"""pkg_avahi command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import typing


class PkgAvahiCommand(Command):
    """The pkg_avahi command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('pkg_avahi', help_string='Setup MDNS using avahi.',
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
                               'pacman', 'avahi', 'nss-mdns')

        # Do setup:
        # Fix missing symlink:
        system_context.execute(location.next_line(), 'symlink',
                               'avahi-daemon.service',
                               'dbus-org.freedesktop.Avahi.service',
                               work_directory='/usr/lib/systemd/system')

        # enable the daemon (actually set up socket activation)
        system_context.execute(location.next_line(), 'systemd_enable',
                               'avahi-daemon.service')

        # Open the firewall for it:
        system_context.execute(location.next_line(), 'net_firewall_open_port', '5353',
                               protocol='udp', comment='Avahi')

        # Edit /etc/nsswitch.conf:
        system_context.execute(location.next_line(), 'sed',
                               '/^hosts\\s*:/ '
                               's/resolve/mdns_minimal [NOTFOUND=return] '
                               'resolve/', '/etc/nsswitch.conf')
