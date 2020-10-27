# -*- coding: utf-8 -*-
"""_clr_dynamic_trust_store_trigger command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.binarymanager import Binaries
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing
import os


class ClrDynamicTrustStoreTriggerCommand(Command):
    """The _clr_dynamic_trust_store_trigger command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_clr_dynamic_trust_store_trigger",
            help_string="Update trust store.",
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
                "/usr/lib/systemd/system/dynamic-trust-store.service"
            )
        ) or not os.path.isfile(system_context.file_name("/usr/bin/clrtrust")):
            return

        run(
            "/usr/bin/clrtrust",
            "generate",
            chroot_helper=self._binary(Binaries.SYSTEMD_NSPAWN),
            chroot=system_context.fs_directory,
        )

        self._execute(
            location,
            system_context,
            "persist_on_usr",
            "dynamic-trust-store",
            "/var/cache/ca-certs",
        )

        os.remove(
            system_context.file_name(
                "/usr/lib/systemd/system/dynamic-trust-store.service"
            )
        )
        os.remove(
            system_context.file_name(
                "/usr/lib/systemd/system/update-triggers.target.wants/dynamic-trust-store.service"
            )
        )
