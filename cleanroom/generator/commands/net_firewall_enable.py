# -*- coding: utf-8 -*-
"""net_firewall_enable command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.helper.archlinux.iptables import enable_firewall


class NetFirewallEnableCommand(Command):
    """The net_firewall_enable command."""

    def __init__(self):
        """Constructor."""
        super().__init__('net_firewall_enable',
                         help='Enable previously configured firewall.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        enable_firewall(location, system_context)
