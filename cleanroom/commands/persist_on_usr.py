# -*- coding: utf-8 -*-
"""persisit_on_usr command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from os.path import dirname
from cleanroom.command import Command
from cleanroom.exceptions import ParseError
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os
import shutil
import typing


class PersistOnUsrCommand(Command):
    """The persist_on_usr command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "persist_on_usr",
            syntax_string="<NAME> <DIRECTORY>",
            help_string="Persist a directory in /usr/lib/persistent",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_arguments_exact(
            location, 2, "{} needs a name and a var directory to move.", *args, **kwargs
        )

        if not args[0]:
            raise ParseError("The name must not be empty!")

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        name = args[0]
        assert name
        directory = args[1]
        assert directory[0] == "/"

        full_directory = system_context.file_name(directory)
        usr_dir = f"/usr/lib/persistent{directory}"
        full_usr_dir = system_context.file_name(usr_dir)
        if not os.path.isdir(full_directory):
            return

        os.makedirs(dirname(full_usr_dir), exist_ok=True)

        if os.path.isdir(full_directory):
            shutil.move(full_directory, full_usr_dir)
        else:
            os.makedirs(full_usr_dir)
        os.symlink(usr_dir, full_directory)

        self._execute(
            location,
            system_context,
            "create",
            f"/usr/lib/tmpfiles.d/{name}.conf",
            f"L {directory} - - - - {usr_dir}\n",
            mode=0o644,
        )
