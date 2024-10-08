# -*- coding: utf-8 -*-
"""strip_development_files command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing

import os


class StripDevelopmentFilesCommand(Command):
    """The strip_development_files Command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "strip_development_files",
            help_string="Strip away development files.",
            file=__file__,
            **services,
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
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        location.set_description("Strip development files")
        self._add_hook(
            location,
            system_context,
            "export",
            "remove",
            "/usr/include/*",
            "/usr/src/*",
            "/usr/share/pkgconfig/*",
            "/usr/lib/pkgconfig/*",
            "/usr/share/aclocal/*",
            "/usr/lib/cmake/*",
            "/usr/share/gir-1.0/*",
            recursive=True,
            force=True,
        )

        # Remove .so symlinks:
        directory = system_context.file_name("/usr/lib")
        for f in os.listdir(directory):
            fullname = os.path.join(directory, f)
            if fullname.endswith("/libnss_files.so"):
                continue
            if fullname.endswith(".a") or (
                fullname.endswith(".so") and os.path.islink(fullname)
            ):
                os.unlink(fullname)
