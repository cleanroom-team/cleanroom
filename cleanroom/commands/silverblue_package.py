# -*- coding: utf-8 -*-
"""Package Fedora Silverblue

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.command import Command
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class PackageSilverblueCommand(Command):
    """The silverblue_package command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "silverblue_package",
            syntax="<VERSION>",
            help_string="Package fedora silverblue.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_arguments_exact(
            location,
            1,
            '"{}" needs a fedora version number to install (or rawhide).',
            *args,
            **kwargs,
        )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        version = args[0]

        run(
            "/usr/bin/ostree",
            "admin",
            "os-init",
            "--sysroot=/clrm/work_dir/fedora",
            f"fedora-{version}",
        )

        run(
            "/usr/bin/ostree",
            "admin",
            "deploy",
            f"--os=fedora-{version}",
            "--karg-proc-cmdline",
            f"fedora:fedora/{version}/x86_64/silverblue",
            "--sysroot=/clrm/work_dir/fedora",
        )
