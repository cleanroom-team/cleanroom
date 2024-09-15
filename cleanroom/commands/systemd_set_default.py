# -*- coding: utf-8 -*-
"""systemd_set_default command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.command import Command
from cleanroom.exceptions import GenerateError
from cleanroom.helper.file import isfile
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class SystemdSetDefaultCommand(Command):
    """The systemd_set_default command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "systemd_set_default",
            syntax="<TARGET>",
            help_string="Set the systemd target to boot into.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_arguments_exact(
            location, 1, '"{}" needs a target name.', *args, **kwargs
        )

    def register_substitutions(self) -> typing.List[typing.Tuple[str, str, str]]:
        return [
            (
                "DEFAULT_BOOT_TARGET",
                "multi-user.target",
                "The systemd target to boot into",
            ),
        ]

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        target = args[0]
        systemd_directory = "/usr/lib/systemd/system/"
        target_path = systemd_directory + args[0]

        if not isfile(system_context, target_path):
            raise GenerateError(
                f'Target "{target}" does not exist or is no file. Can not use as default target.'
            )

        default = "default.target"
        default_path = systemd_directory + "default.target"

        self._execute(location, system_context, "remove", default_path, force=True)
        self._execute(
            location.next_line(),
            system_context,
            "symlink",
            target,
            default,
            work_directory=systemd_directory,
        )

        system_context.set_substitution("DEFAULT_BOOT_TARGET", target)
