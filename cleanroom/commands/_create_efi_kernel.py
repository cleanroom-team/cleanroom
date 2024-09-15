# -*- coding: utf-8 -*-
"""create_efi_kernel command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.exceptions import GenerateError
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext
from cleanroom.printer import debug, trace

from glob import glob
import os
import typing


def _create_initrd(directory: str, *files: str) -> str:
    target = os.path.join(directory, "initrd")
    with open(target, "wb") as target_file:
        for f in files:
            with open(f, "rb") as source_file:
                target_file.write(source_file.read())

    # compress the entire initrd:
    debug("Compressing initrd with gzip")
    run("gzip", "-9", target)
    # os.remove(target) ## Gzip kills the uncompressed file!
    os.rename(f"{target}.gz", target)

    return target


def _get_initrd_parts(location: Location, path: str) -> typing.List[str]:
    initrd_parts: typing.List[str] = []
    for f in glob(os.path.join(path, "*")):
        if os.path.isfile(f):
            initrd_parts.append(f)
    if not initrd_parts:
        raise GenerateError(
            f'No initrd-parts found in directory "{path}".', location=location
        )
    initrd_parts.sort()
    for ip in initrd_parts:
        trace(f"    Adding into initrd: {ip} ...")
    return initrd_parts


class CreateEfiKernelCommand(Command):
    """The create_efi_kernel command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "create_efi_kernel",
            syntax="<EFI_KERNEL> kernel=<KERNEL> "
            "initrd_directory=<INITRD_PARTS_DIRECTORY> "
            "commandline=<KERNEL_COMMANDLINE>",
            help_string="Create a efi kernel with built-in initrd.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_args_exact(
            location, 1, '"{}" needs a efi kernel image to create.', *args
        )
        self._validate_kwargs(
            location, ("kernel", "initrd_directory", "commandline"), **kwargs
        )
        self._require_kwargs(
            location, ("kernel", "initrd_directory", "commandline"), **kwargs
        )

    def _validate_files(self, location: Location, *files: str) -> None:
        for f in files:
            if f and not os.path.isfile(f):
                raise GenerateError(
                    f'"{self.name}": referenced file "{f}" does not exist.',
                    location=location,
                )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        output = args[0]
        kernel = kwargs.get("kernel", "")
        initrd_files = _get_initrd_parts(
            location, system_context.initrd_parts_directory
        )
        cmdline_input = kwargs.get("commandline", "")
        osrelease_file = system_context.file_name("/usr/lib/os-release")
        efistub = system_context.file_name(
            "/usr/lib/systemd/boot/efi/" "linuxx64.efi.stub"
        )

        debug(f"{self.name}: Kernel   : {kernel}.")
        debug(f"{self.name}: Initrd   : {initrd_files}.")
        debug(f"{self.name}: cmdline  : {cmdline_input}.")
        debug(f"{self.name}: osrelease: {osrelease_file}.")
        debug(f"{self.name}: efistub  : {efistub}.")

        self._validate_files(location, kernel, *initrd_files, osrelease_file, efistub)

        initrd = _create_initrd(system_context.boot_directory, *initrd_files)

        run(
            self._binary(Binaries.UKIFY),
            "build",
            "--no-measure",
            "--no-sign-kernel",
            f"--linux={kernel}",
            f"--cmdline={cmdline_input}",
            f"--os-release=@{osrelease_file}",
            f"--initrd={initrd}",
            f"--stub={efistub}",
            f"--output={output}",
        )
