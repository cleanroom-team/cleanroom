# -*- coding: utf-8 -*-
"""net_firewall_open_port command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.exceptions import ParseError
from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.helper.archlinux.iptables import open_port
from cleanroom.generator.systemcontext import SystemContext

import typing


class NetFirewallOpenPortCommand(Command):
    """The net_firewall_open_port command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('net_firewall_open_port',
                         syntax='<PORT> [protocol=(tcp|udp)] [comment=<TEXT>]',
                         help_string='Open a port in the firewall.', file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs a port to open.',
                                  *args)
        self._validate_kwargs(location, ('protocol', 'comment'), **kwargs)

        protocol = kwargs.get('protocol', 'tcp')
        if protocol != 'tcp' and protocol != 'udp':
            raise ParseError('"{}" only supports protocols "tcp" and "udp".'
                             .format(self.name()), location=location)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        protocol = kwargs.get('protocol', 'tcp')
        comment = kwargs.get('comment', None)
        open_port(location, system_context, args[0],
                  protocol=protocol, comment=comment)
