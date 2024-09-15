# -*- coding: utf-8 -*-
"""net_firewall_enable command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.command import Command
from cleanroom.helper.archlinux.iptables import firewall_type
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing
import os


class NetFirewallEnableCommand(Command):
    """The net_firewall_enable command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "net_firewall_enable",
            help_string="Enable previously configured firewall.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        assert firewall_type(system_context) == "iptables"
        location.set_description("Enable firewall")
        to_enable: typing.List[str] = []
        if os.path.exists(
            system_context.file_name("/usr/lib/systemd/system/iptables.service")
        ):
            to_enable.append("iptables.service")
        if os.path.exists(
            system_context.file_name("/usr/lib/systemd/system/ip6tables.service")
        ):
            to_enable.append("ip6tables.service")
        if os.path.exists(
            system_context.file_name("/usr/lib/systemd/system/iptables-restore.service")
        ):
            to_enable.append("iptables-restore.service")

        self._execute(
            location,
            system_context,
            "systemd_enable",
            *to_enable,
        )
