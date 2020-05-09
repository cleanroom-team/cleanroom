# -*- coding: utf-8 -*-
"""sshd_install_knownhosts command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.exceptions import GenerateError
from cleanroom.helper.file import isdir
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class SshdInstallKnownhostsCommand(Command):
    """The sshd_install_knownhosts command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "sshd_install_knownhosts",
            help_string="Install system wide knownhosts file.",
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
        # FIXME: Implement this!
        # self._validate_key_directory(location, key_directory)
        if not isdir(system_context, "/etc/ssh"):
            raise GenerateError(
                '"{}": No /etc/ssh directory found in system.'.format(self.name),
                location=location,
            )
