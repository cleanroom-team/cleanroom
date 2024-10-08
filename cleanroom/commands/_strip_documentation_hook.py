# -*- coding: utf-8 -*-
"""_strip_documentation_hook command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.printer import debug
from cleanroom.systemcontext import SystemContext

import os.path
import typing


class StripDocumentationHookCommand(Command):
    """The strip_documentation Command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_strip_documentation_hook",
            help_string="Strip away documentation files (hook).",
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
        location.set_description("Strip documentation files")
        to_remove = ["/usr/share/doc/*", "/usr/share/gtk-doc/html", "/usr/share/help/*"]
        if not os.path.exists(system_context.file_name("/usr/bin/man")):
            debug("No /usr/bin/man: Removing man pages.")
            to_remove += ["/usr/share/man/*"]
        if not os.path.exists(system_context.file_name("/usr/bin/info")):
            debug("No /usr/bin/info: Removing info pages.")
            to_remove += ["/usr/share/info/*"]
        self._execute(
            location, system_context, "remove", *to_remove, recursive=True, force=True
        )
