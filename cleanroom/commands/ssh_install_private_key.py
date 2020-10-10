# -*- coding: utf-8 -*-
"""ssh_install_private_key command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.exceptions import GenerateError
from cleanroom.helper.file import chmod, chown, exists, isdir, makedirs
from cleanroom.helper.user import UserHelper
from cleanroom.location import Location
from cleanroom.printer import debug, trace
from cleanroom.systemcontext import SystemContext

import os.path
import typing


class SshInstallPrivateKeyCommand(Command):
    """The ssh_install_private_key command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "ssh_install_private_key",
            syntax="<USER> <KEYFILE> [include_public_key=False]",
            help_string="Install <KEYFILE> as private key for <USER>.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_args_exact(
            location, 2, '"{}" needs a user and a keyfile.', *args
        )
        self._validate_kwargs(location, ("include_public_key",), **kwargs)

    def _check_or_create_directory(
        self,
        location: Location,
        system_context: SystemContext,
        directory: str,
        **kwargs: typing.Any,
    ) -> None:
        if not exists(system_context, directory):
            makedirs(system_context, directory, **kwargs)
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
        user_name = args[0]
        key_file = args[1]

        user = UserHelper.user_data(
            user_name, root_directory=system_context.fs_directory
        )
        if user is None:
            raise GenerateError(
                f'"{self.name}" could not find user "{user_name}".',
                location=location,
            )

        debug(f'Installing "{key_file}" to user "{user_name}" ({user.home}).')

        self._check_or_create_directory(
            location,
            system_context,
            user.home,
            mode=0o750,
            user=user.uid,
            group=user.gid,
        )
        ssh_directory = os.path.join(user.home, ".ssh")
        self._check_or_create_directory(
            location,
            system_context,
            ssh_directory,
            mode=0o600,
            user=user.uid,
            group=user.gid,
        )

        installed_key_file = os.path.join(ssh_directory, os.path.basename(key_file))

        self._execute(
            location.next_line(),
            system_context,
            "copy",
            key_file,
            installed_key_file,
            from_outside=True,
        )
        trace("Copied key.")
        chown(system_context, user.uid, user.gid, installed_key_file)
        trace("Ownership adjusted.")
        chmod(system_context, 0o600, installed_key_file)
        trace("Mode adjusted.")

        if kwargs.get("include_public_key", False):
            public_key = key_file + ".pub"
            installed_public_key = os.path.join(
                ssh_directory, os.path.basename(public_key)
            )

            self._execute(
                location.next_line(),
                system_context,
                "copy",
                public_key,
                installed_public_key,
                from_outside=True,
            )
            trace("Copied key.")
            chown(system_context, user.uid, user.gid, installed_public_key)
            trace("Ownership adjusted.")
            chmod(system_context, 0o644, installed_public_key)
            trace("Mode adjusted.")
