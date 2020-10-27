# -*- coding: utf-8 -*-
"""_clr_hwdb_update_trigger command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing
import os


class ClrHwdbUpdateTriggerCommand(Command):
    """The _clr_hwdb_update_trigger command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_clr_hwdb_update_trigger",
            help_string="Update HWDB.",
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
        if not os.path.isfile(
            system_context.file_name(
                "/usr/lib/systemd/system/hwdb-update-trigger.service"
            )
        ):
            return

        run(
            "/usr/bin/systemd-hwdb",
            "update",
            f"--root={system_context.fs_directory}",
            "--usr",
        )

        os.remove(
            system_context.file_name(
                "/usr/lib/systemd/system/hwdb-update-trigger.service"
            )
        )
