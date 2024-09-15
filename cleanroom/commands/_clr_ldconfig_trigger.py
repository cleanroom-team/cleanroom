# -*- coding: utf-8 -*-
"""_clr_ldconfig_trigger command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing
import os


class ClrLdconfigTriggerCommand(Command):
    """The _clr_ldconfig_trigger command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_clr_ldconfig_trigger",
            help_string="Update ldconfig caches.",
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
        if not os.path.isfile(
            system_context.file_name("/usr/lib/systemd/system/ldconfig-trigger.service")
        ):
            return

        run(
            "/usr/bin/ldconfig",
            "-X",
            chroot_helper=self._binary(Binaries.SYSTEMD_NSPAWN),
            chroot=system_context.fs_directory,
        )

        if os.path.isfile(system_context.file_name("/usr/lib/tmpfiles.d/var.conf")):
            self._execute(
                location,
                system_context,
                "sed",
                "/\\/var\\/cache\\/ldconfig/ d",
                "/usr/lib/tmpfiles.d/var.conf",
            )

        self._execute(
            location,
            system_context,
            "sed",
            "/\\/var\\/cache\\/ldconfig/ d",
            "/usr/lib/tmpfiles.d/filesystem.conf",
        )

        self._execute(
            location,
            system_context,
            "persist_on_usr",
            "ldconfig-trigger",
            "/var/cache/ldconfig",
        )

        os.remove(
            system_context.file_name("/usr/lib/systemd/system/ldconfig-trigger.service")
        )
