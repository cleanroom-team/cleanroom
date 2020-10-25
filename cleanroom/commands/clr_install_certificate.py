# -*- coding: utf-8 -*-
"""clr_install_certificate command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.printer import trace
from cleanroom.systemcontext import SystemContext

import os
import os.path
from shutil import copy2
from tempfile import TemporaryDirectory
import typing


class InstallCertificatesCommand(Command):
    """The clr_install_certificate command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "clr_install_certificate",
            syntax="<CA_CERT>+",
            help_string="Install CA certificates.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_arguments_at_least(
            location,
            1,
            '"{}" needs at least one ca certificate to add',
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
        cas: typing.List[str] = []
        with TemporaryDirectory(dir=system_context.fs_directory) as tmpdir:
            for f in args:
                source = (
                    f
                    if os.path.isabs(f)
                    else os.path.join(
                        system_context.systems_definition_directory or "", f
                    )
                )
                ca_file = os.path.join(tmpdir, os.path.basename(source))

                trace(f"Copying CA from {source} to {ca_file}.")
                copy2(source, ca_file)
                os.chmod(ca_file, mode=0o644)

                cas.append(
                    os.path.join(
                        "/", os.path.basename(tmpdir), os.path.basename(source)
                    )
                )

            run(
                "/usr/bin/clrtrust",
                "add",
                *cas,
                chroot=system_context.fs_directory,
                chroot_helper=self._binary(Binaries.SYSTEMD_NSPAWN),
            )
