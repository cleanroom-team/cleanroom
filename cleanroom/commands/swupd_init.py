# -*- coding: utf-8 -*-
"""swupd_init command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.exceptions import GenerateError, ParseError
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.printer import verbose
from cleanroom.systemcontext import SystemContext

import os
from textwrap import dedent
import typing


class swupd_initCommand(Command):
    """The swupd_init command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "swupd_init",
            target_distribution="clr",
            help_string="Run swupd_init to initialize clearlinux installation.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        if not self._binary(Binaries.SWUPD):
            raise ParseError("No swupd_init binary was found.")

        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        ## validate package type:
        if system_context.substitution("CLRM_PACKAGE_TYPE", ""):
            raise GenerateError(
                "Trying to run swupd_init on a system that already has a CLRM_PACKAGE_TYPE defined."
            )
        system_context.set_substitution("CLRM_PACKAGE_TYPE", "swupd")
        system_context.set_substitution("DISTRO_PRETTY_NAME", "Cleanroom - CLR")

        run(
            self._binary(Binaries.SWUPD),
            "autoupdate",
            f"--path={system_context.fs_directory}",
            "--disable",
            "--no-progress",
            returncode=28,
        )

        # Setup update-helper so that swupd os-install will actually work:
        os.makedirs(system_context.file_name("/usr/bin"))
        with open(system_context.file_name("/usr/bin/update-helper"), "wb") as fd:
            fd.write(
                dedent(
                    """\
                        #!/usr/bin/sh
                        exit 0
                    """
                ).encode("utf-8")
            )
        os.chmod(system_context.file_name("/usr/bin/update-helper"), 0o755)

        run(
            self._binary(Binaries.SWUPD),
            "os-install",
            f"--path={system_context.fs_directory}",
            "--skip-optional",
            "--no-progress",
        )

        system_context.set_substitution("INITRD_GENERATOR", "clr")

        location.set_description("Move systemd files into /usr")
        self._add_hook(location, system_context, "_teardown", "systemd_cleanup")

        with open(system_context.file_name("/usr/lib/os-release"), "r") as osr:
            for l in osr:
                l = l.strip()
                if l.startswith("BUILD_ID="):
                    build_id = l[9:]
                    verbose(f"Installed {build_id}.")
                    system_context.set_substitution("DISTRO_VERSION_ID", build_id)
                    system_context.set_substitution("DISTRO_VERSION", build_id)

        self._execute(location.next_line(), system_context, "create_os_release")
