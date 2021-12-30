# -*- coding: utf-8 -*-
"""ensure_ldconfig command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os
import typing


class EnsureLdconfigCommand(Command):
    """The ensure_ldconfig command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "ensure_ldconfig",
            help_string="Ensure that ldconfig is run.",
            file=__file__,
            **services
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
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        bin_ldconfig = "/usr/bin/ldconfig"
        sbin_ldconfig = "/usr/sbin/ldconfig"
        ldconfig = (
            bin_ldconfig
            if os.path.isfile(system_context.file_name(bin_ldconfig))
            else sbin_ldconfig
        )

        assert os.path.exists(system_context.file_name(ldconfig))

        location.set_description("Run ldconfig")
        self._add_hook(
            location,
            system_context,
            "export",
            "run",
            ldconfig,
            "-X",
            inside=True,
        )
        location.set_description("Remove ldconfig data")
        # self._add_hook(location, system_context,
        #                'export', 'remove', '/usr/bin/ldconfig')
        location.set_description("Remove ldconfig related services")
        self._add_hook(
            location,
            system_context,
            "export",
            "remove",
            "/usr/lib/systemd/system/*/ldconfig.service",
            "/usr/lib/systemd/system/ldconfig.service",
            force=True,
        )
