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
        os_release = 'NAME="{}"\n'.format(
            system_context.substitution_expanded("DISTRO_NAME", "")
        )
        os_release += 'PRETTY_NAME="{}"\n'.format(
            system_context.substitution_expanded("DISTRO_PRETTY_NAME", "")
        )
        os_release += 'ID="{}"\n'.format(
            system_context.substitution_expanded("DISTRO_ID", "")
        )
        os_release += 'ID_LIKE="{}"\n'.format(
            system_context.substitution_expanded("DISTRO_ID_LIKE", "")
        )
        os_release += 'ANSI_COLOR="{}"\n'.format(
            system_context.substitution_expanded("DISTRO_ANSI_COLOR", "")
        )
        os_release += 'HOME_URL="{}"\n'.format(
            system_context.substitution_expanded("DISTRO_HOME_URL", "")
        )
        os_release += 'SUPPORT_URL="{}"\n'.format(
            system_context.substitution_expanded("DISTRO_SUPPORT_URL", "")
        )
        os_release += 'BUG_REPORT_URL="{}"\n'.format(
            system_context.substitution_expanded("DISTRO_BUG_URL", "")
        )
        os_release += 'VERSION="{}"\n'.format(
            system_context.substitution_expanded("DISTRO_VERSION", "")
        )
        os_release += 'VERSION_ID="{}"\n'.format(
            system_context.substitution_expanded("DISTRO_VERSION_ID", "")
        )

        self._execute(
            location,
            system_context,
            "create",
            "/usr/lib/os-release",
            os_release,
            force=True,
            mode=0o644,
        )
