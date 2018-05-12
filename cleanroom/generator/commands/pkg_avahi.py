# -*- coding: utf-8 -*-
"""pkg_avahi command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command


class PkgAvahiCommand(Command):
    """The pkg_avahi command."""

    def __init__(self):
        """Constructor."""
        super().__init__('pkg_avahi', help='Setup MDNS using avahi.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        system_context.execute(location, 'pacman', 'avahi', 'nss-mdns')

        # Do setup:
        # Fix missing symlink:
        system_context.execute(location, 'symlink',
                               'avahi-daemon.service',
                               'dbus-org.freedesktop.Avahi.service',
                               base_directory='/usr/lib/systemd/system')

        # enable the daemon (actually set up socket activation)
        system_context.execute(location, 'systemd_enable',
                               'avahi-daemon.service')

        # Open the firewall for it:
        system_context.execute(location, 'net_firewall_open_port', '5353',
                               protocol='udp', comment='Avahi')

        # Edit /etc/nsswitch.conf:
        system_context.execute(location, 'sed',
                               '/^hosts\\s*:/ '
                               's/resolve/mdns_minimal [NOTFOUND=return] '
                               'resolve/', '/etc/nsswitch.conf')
