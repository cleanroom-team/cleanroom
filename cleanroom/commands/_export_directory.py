# -*- coding: utf-8 -*-
"""_export_directory command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing
import os.path


class ExportDirectoryCommand(Command):
    """The _export_directory command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_export_directory",
            syntax="<DIRECTORY> "
            "compression=<zstd> "
            "compression_level=<5> "
            "repository=<REPOSITORY_PATH>",
            help_string="Export a directory from cleanroom.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_args_exact(
            location,
            1,
            '"{}" needs a borg repository directory ' "to export into.",
            *args
        )
        self._validate_kwargs(
            location, ("compression", "compression_level", "repository"), **kwargs
        )
        self._require_kwargs(location, ("repository",), **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        export_directory = args[0]
        export_repository = os.path.join(
            system_context.repository_base_directory, kwargs.get("repository", "")
        )

        backup_name = system_context.system_name + "-" + system_context.timestamp

        run(
            self._service("binary_manager").binary(Binaries.BORG),
            "create",
            "--compression",
            "{},{}".format(
                kwargs.get("compression", "zstd"), kwargs.get("compression_level", 5)
            ),
            "--numeric-owner",
            "--noatime",
            "{}::{}".format(export_repository, backup_name),
            ".",
            work_directory=export_directory,
        )
