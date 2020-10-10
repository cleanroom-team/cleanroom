# -*- coding: utf-8 -*-
"""ssh_allow_login command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.command import Command
from cleanroom.exceptions import GenerateError
from cleanroom.helper.file import chmod, chown, exists, isdir, read_file
from cleanroom.helper.user import UserHelper
from cleanroom.location import Location
from cleanroom.printer import info, trace
from cleanroom.systemcontext import SystemContext

import os.path
import typing


class SshAllowLoginCommand(Command):
    """The ssh_allow_login command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "ssh_allow_login",
            syntax="<USER> <PUBLIC_KEYFILE> " "options=<OPTIONS>",
            help_string="Authorize <PUBLIC_KEYFILE> to log in " "as <USER>.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_args_exact(
            location, 2, '"{}" needs a user and ' "a public keyfile.", *args
        )
        self._validate_kwargs(location, ("options",), **kwargs)

    def _check_or_create_directory(
        self,
        location: Location,
        system_context: SystemContext,
        directory: str,
        **kwargs: typing.Any,
    ) -> None:
        if not exists(system_context, directory):
            self._execute(
                location.next_line(), system_context, "mkdir", directory, **kwargs
            )
            return
        if not isdir(system_context, directory):
            raise GenerateError(
                f'"{self.name}" needs directory "{directory}", but that exists and is not a directory.',
                location=location,
            )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        user = args[0]
        keyfile = args[1]

        info(f"Adding ssh key to {user}'s authorized_keys file.")
        data = UserHelper.user_data(user, root_directory=system_context.fs_directory)
        if data is None:
            raise GenerateError(
                f'"{self.name}" could not find user "{user}".',
                location=location,
            )

        trace(f"{user} mapping: UID {data.uid}, GID {data.gid}, home: {data.home}.")
        self._check_or_create_directory(
            location,
            system_context,
            data.home,
            mode=0o750,
            user=data.uid,
            group=data.gid,
        )
        ssh_directory = os.path.join(data.home, ".ssh")
        self._check_or_create_directory(
            location,
            system_context,
            ssh_directory,
            mode=0o700,
            user=data.uid,
            group=data.gid,
        )

        key = read_file(system_context, keyfile, outside=True).decode("utf-8")

        authorized_file = os.path.join(ssh_directory, "authorized_keys")
        line = ""

        options = kwargs.get("options", "")

        if options:
            line = options + " " + key + "\n"
        else:
            line += key + "\n"

        self._execute(
            location.next_line(),
            system_context,
            "append",
            authorized_file,
            line,
            force=True,
        )
        chown(system_context, data.uid, data.gid, authorized_file)
        chmod(system_context, 0o600, authorized_file)
