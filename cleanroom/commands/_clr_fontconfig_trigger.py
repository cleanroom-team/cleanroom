# -*- coding: utf-8 -*-
"""_clr_fontconfig_trigger command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing
import os


class ClrFontconfigTriggerCommand(Command):
    """The _clr_fontconfig_trigger command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "clr_fontconfig_trigger",
            help_string="Update fontconfig caches.",
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
                "/usr/lib/systemd/system/fontconfig-trigger.service"
            )
        ) or not os.path.isfile(system_context.file_name("/usr/bin/fc-cache")):
            return

        run(
            "/usr/bin/fc-cache",
            chroot_helper=self._binary(Binaries.SYSTEMD_NSPAWN),
            chroot=system_context.fs_directory,
        )

        self._execute(
            location,
            system_context,
            "persist_on_usr",
            "fontconfig-trigger",
            "/var/cache/fontconfig",
        )

        os.remove(
            system_context.file_name(
                "/usr/lib/systemd/system/fontconfig-trigger.service"
            )
        )
        os.remove(
            system_context.file_name(
                "/usr/lib/systemd/system/update-triggers.target.wants/fontconfig-trigger.service"
            )
        )
