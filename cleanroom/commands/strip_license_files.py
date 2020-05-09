# -*- coding: utf-8 -*-
"""strip_license_files command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class StripLicenseFilesCommand(Command):
    """The strip_license_files Command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "strip_license_files",
            help_string="Strip away license files.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        location.set_description("Strip license files")
        self._add_hook(
            location,
            system_context,
            "export",
            "remove",
            "/usr/share/licenses/*",
            recursive=True,
            force=True,
        )
