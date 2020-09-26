# -*- coding: utf-8 -*-
"""firejail_apps command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.exceptions import GenerateError, ParseError
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os.path
import typing


class FirejailAppsConfigureCommand(Command):
    """The firejail_apps command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "firejail_apps",
            syntax="<APP>+",
            help_string="Firejail applications.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        if not args:
            raise ParseError(
                f'"{self.name}" does need at least one application.', location=location,
            )
        self._validate_arguments_at_least(
            location, 1, '"{}" needs at least one application.', *args
        )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        for a in args:
            location.set_description(f"Processing application {a}.")
            desktop_file = f"/usr/share/applications/{a}.desktop"
            if not os.path.exists(system_context.file_name(desktop_file)):
                raise GenerateError(
                    f'Desktop file "{desktop_file}" not found.', location=location,
                )
            self._execute(
                location.next_line(),
                system_context,
                "sed",
                "/^Exec=.*$$/ s!^Exec=!Exec=/usr/bin/firejail !",
                desktop_file,
            )
