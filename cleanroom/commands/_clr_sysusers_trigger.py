# -*- coding: utf-8 -*-
"""_clr_sysusers_trigger command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.binarymanager import Binaries
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import shutil
import typing
import os


class ClrSysusersTriggerCommand(Command):
    """The _clr_sysusers_trigger command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_clr_sysusers_trigger",
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
            system_context.file_name("/usr/lib/systemd/system/sysusers-trigger.service")
        ):
            return

        run(
            "/usr/bin/systemd-sysusers",
            chroot_helper=self._binary(Binaries.SYSTEMD_NSPAWN),
            chroot=system_context.fs_directory,
        )

        shutil.rmtree(system_context.file_name("/usr/lib/sysusers.d"))
        os.remove(system_context.file_name("/usr/bin/systemd-sysusers"))
        os.remove(
            system_context.file_name("/usr/lib/systemd/system/sysusers-trigger.service")
        )
