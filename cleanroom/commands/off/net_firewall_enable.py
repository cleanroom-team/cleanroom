# -*- coding: utf-8 -*-
"""net_firewall_enable command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.helper.archlinux.iptables import enable_firewall
from cleanroom.generator.systemcontext import SystemContext

import typing


class NetFirewallEnableCommand(Command):
    """The net_firewall_enable command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('net_firewall_enable',
                         help_string='Enable previously configured firewall.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        enable_firewall(location, system_context)
