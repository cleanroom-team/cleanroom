# -*- coding: utf-8 -*-
"""ensure_no_update_service command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class EnsureNoUpdateServiceCommand(Command):
    """The ensure_no_update_service command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "ensure_no_update_service",
            help_string="Set up system for a read-only /usr partition.",
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
        # Remove unnecessary systemd-services:
        self._execute(
            location.next_line(),
            system_context,
            "remove",
            "/usr/lib/systemd/system/systemd-update-done.service",
            "/usr/lib/systemd/system/" "system-update-cleanup.service",
            "/usr/lib/systemd/system/system-update.target",
            "/usr/lib/systemd/system/system-update-pre.target",
            "/usr/lib/systemd/system-generators/" "systemd-system-update-generator",
            "/usr/lib/systemd/systemd-update-done",
            force=True,
        )
