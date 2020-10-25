# -*- coding: utf-8 -*-
"""ensure_hwdb command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os
import typing


class EnsureHwdbCommand(Command):
    """The ensure_hwdb command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "ensure_hwdb",
            help_string="Make sure hwdb is installed.",
            file=__file__,
            **services
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
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        assert os.path.exists(system_context.file_name("/usr/bin/systemd-hwdb"))

        location.set_description("Update HWDB")
        self._add_hook(
            location,
            system_context,
            "export",
            "run",
            "/usr/bin/systemd-hwdb",
            "--usr",
            "update",
            inside=True,
        )
        location.set_description("Remove HWDB data")
        self._add_hook(
            location, system_context, "export", "remove", "/usr/bin/systemd-hwdb"
        )
        location.set_description("Remove HWDB related services")
        self._add_hook(
            location,
            system_context,
            "export",
            "remove",
            "/usr/lib/systemd/system/*/systemd-hwdb-update.service",
            "/usr/lib/systemd/system/systemd-hwdb-update.service",
            force=True,
        )
