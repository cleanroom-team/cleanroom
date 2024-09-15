# -*- coding: utf-8 -*-
"""_clr_catalog_trigger command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.command import Command
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing
import os


class ClrCatalogTriggerCommand(Command):
    """The _clr_catalog_trigger command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_clr_catalog_trigger",
            help_string="Update journal catalog.",
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
        if not os.path.exists(
            system_context.file_name("/usr/lib/systemd/system/catalog-trigger.service")
        ):
            return

        self._execute(
            location,
            system_context,
            "sed",
            "/\\/var\\/lib\\/systemd\\/catalog/ d",
            "/usr/lib/tmpfiles.d/filesystem.conf",
        )

        run(
            "/usr/bin/journalctl",
            f"--root={system_context.fs_directory}",
            "--update-catalog",
        )

        self._execute(
            location,
            system_context,
            "persist_on_usr",
            "catalog-trigger",
            "/var/lib/systemd/catalog",
        )

        os.remove(
            system_context.file_name("/usr/lib/systemd/system/catalog-trigger.service")
        )
