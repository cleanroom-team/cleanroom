# -*- coding: utf-8 -*-
"""net_firewall_open_port command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.exceptions import ParseError
from cleanroom.helper.archlinux.iptables import open_port
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class NetFirewallOpenPortCommand(Command):
    """The net_firewall_open_port command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "net_firewall_open_port",
            syntax="<PORT> [protocol=(tcp|udp)] [comment=<TEXT>]",
            help_string="Open a port in the firewall.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs a port to open.', *args)
        self._validate_kwargs(location, ("protocol", "comment"), **kwargs)

        protocol = kwargs.get("protocol", "tcp")
        if protocol != "tcp" and protocol != "udp":
            raise ParseError(
                '"{}" only supports protocols "tcp" and "udp".'.format(self.name),
                location=location,
            )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        protocol = kwargs.get("protocol", "tcp")
        comment = kwargs.get("comment", "")
        open_port(system_context, args[0], protocol=protocol, comment=comment)
