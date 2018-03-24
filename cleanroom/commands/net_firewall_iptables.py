# -*- coding: utf-8 -*-
"""net_firewall_iptables command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.helper.archlinux.iptables as fw


class MoveCommand(cmd.Command):
    """The net_firewall_iptables command."""

    def __init__(self):
        """Constructor."""
        super().__init__('net_firewall_iptables',
                         help='Set up basic iptables firewall.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        return self._validate_no_arguments(location, args, kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        fw.install(system_context)
