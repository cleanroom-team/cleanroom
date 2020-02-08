# -*- coding: utf-8 -*-
"""pkg_usbguard command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.helper.file import create_file remove
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import textwrap
import typing


class PkgAvahiCommand(Command):
    """The pkg_usbguard command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__('pkg_usbguard',
                         help_string='Install usbguard',
                         file=__file__, **services)

    def validate(self, location: Location,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        self._execute(location, system_context, 'pacman', 'usbguard')

        # Do setup:
        # enable the daemon (actually set up socket activation)
        self._execute(location.next_line(), system_context,
                      'systemd_enable', 'usbguard-dbus.service')

        create_file(system_context, '/usr/lib/tmpfiles.d/usbguard.conf',
                    textwrap.dedent('''\
                    d /var/log/usbguard 0750 root root - -

                    d /var/lib/usbguard 0750 root root - -
                    d /var/lib/usbguard/IPCAccessControl.d 0755 root root - -
                    f /var/lib/usbguard/rules.conf 0600 root root - -
                    ''').encode('utf-8'))

        self._execute(location.next_line(), system_context,
                      'sed', '/RuleFile=\/etc/ cRuleFile=/var/lib/usbguard/rules.conf',
                      '/etc/usbguard/usbguard-daemon.conf')
        self._execute(location.next_line(), system_context,
                      'sed', '/IPCAccessControlFiles=\/etc/ cIPCAccessControlFiles=/var/lib/usbguard/IPCAccessControl.d',
                       '/etc/usbguard/usbguard-daemon.conf')

        remove(system_context,
               '/etc/usbguard/rules.conf',
               '/etc/usbguard/IPCAccessControl.d',
               recursive=True)

