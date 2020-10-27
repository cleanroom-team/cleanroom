# -*- coding: utf-8 -*-
"""_clr_glib_schemas_trigger command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.binarymanager import Binaries
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing
import os


class ClrGlibSchemasTriggerCommand(Command):
    """The _clr_glib_schemas_trigger command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_clr_glib_schemas_trigger",
            help_string="Update glib schemas.",
            file=__file__,
            **services,
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
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        if not os.path.exists(
            system_context.file_name(
                "/usr/lib/systemd/system/glib-schemas-trigger.service"
            )
        ):
            return

        os.makedirs(
            system_context.file_name("/var/cache/glib-2.0/schemas"), exist_ok=True
        )
        run(
            "/usr/libexec/glib-compile-schemas",
            "--targetdir=/var/cache/glib-2.0/schemas",
            "/usr/share/glib-2.0/schemas",
            chroot_helper=self._binary(Binaries.SYSTEMD_NSPAWN),
            chroot=system_context.fs_directory,
        )

        self._execute(
            location,
            system_context,
            "persist_on_usr",
            "glib-schemas-trigger",
            "/var/cache/glib-2.0",
        )

        os.remove(system_context.file_name("/usr/lib/tmpfiles.d/glib.conf"))
        os.remove(system_context.file_name("/usr/libexec/glib-compile-schemas"))
        os.remove(
            system_context.file_name(
                "/usr/lib/systemd/system/glib-schemas-trigger.service"
            )
        )
        os.remove(
            system_context.file_name(
                "/usr/lib/systemd/system/update-triggers.target.wants/glib-schemas-trigger.service"
            )
        )
