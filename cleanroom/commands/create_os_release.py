# -*- coding: utf-8 -*-
"""create_os_release command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class CreateOsReleaseCommand(Command):
    """The create_os_release command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "create_os_release",
            syntax="",
            help_string="Create os release file.",
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
        os_release = (
            f'NAME="{system_context.substitution_expanded("DISTRO_NAME", "")}"\n'
        )
        os_release += f'PRETTY_NAME="{system_context.substitution_expanded("DISTRO_PRETTY_NAME", "")}"\n'
        os_release += f'ID="{system_context.substitution_expanded("DISTRO_ID", "")}"\n'
        os_release += (
            f'ID_LIKE="{system_context.substitution_expanded("DISTRO_ID_LIKE", "")}"\n'
        )
        os_release += f'ANSI_COLOR="{system_context.substitution_expanded("DISTRO_ANSI_COLOR", "")}"\n'
        os_release += f'HOME_URL="{system_context.substitution_expanded("DISTRO_HOME_URL", "")}"\n'
        os_release += f'SUPPORT_URL="{system_context.substitution_expanded("DISTRO_SUPPORT_URL", "")}"\n'
        os_release += f'BUG_REPORT_URL="{system_context.substitution_expanded("DISTRO_BUG_URL", "")}"\n'
        os_release += (
            f'VERSION="{system_context.substitution_expanded("DISTRO_VERSION", "")}"\n'
        )
        os_release += f'VERSION_ID="{system_context.substitution_expanded("DISTRO_VERSION_ID", "")}"\n'
        os_release += f'IMAGE_ID="{system_context.substitution_expanded("DISTRO_VERSION_ID", "")}"\n'
        os_release += f'IMAGE_VERSION="{system_context.substitution_expanded("DISTRO_VERSION_ID", "")}"\n'

        self._execute(
            location,
            system_context,
            "create",
            "/usr/lib/os-release",
            os_release,
            force=True,
            mode=0o644,
        )
