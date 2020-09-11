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
import tempfile
import typing


def _create_initrd(directory: str, *files: str) -> str:
    target = os.path.join(directory, "initrd")
    with open(target, "wb") as target_file:
        for f in files:
            with open(f, "rb") as source_file:
                target_file.write(source_file.read())
    return target


def _create_cmdline_file(directory: str, cmdline: str) -> str:
    target = os.path.join(directory, "cmdline")
    with open(target, "wb") as cmdline_file:
        cmdline_file.write(cmdline.encode("utf-8"))
        cmdline_file.write(b"\0\0")
    return target


def _get_initrd_parts(location: Location, path: str) -> typing.List[str]:
    if not path:
        raise GenerateError("No initrd-parts directory.", location=location)

    initrd_parts: typing.List[str] = []
    for f in glob(os.path.join(path, "*")):
        if os.path.isfile(f):
            initrd_parts.append(f)
    if not initrd_parts:
        raise GenerateError(
            'No initrd-parts found in directory "{}".'.format(path), location=location
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
                    '"{}": referenced file "{}" does not exist.'.format(self.name, f),
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
        initrd_directory = kwargs.get(
            "initrd", os.path.join(system_context.boot_directory, "initrd-parts")
        )
        initrd_files = _get_initrd_parts(location, initrd_directory)
        cmdline_input = kwargs.get("commandline", "")
        osrelease_file = system_context.file_name("/usr/lib/os-release")
        efistub = system_context.file_name(
            "/usr/lib/systemd/boot/efi/" "linuxx64.efi.stub"
        )

        debug("{}: Kernel   : {}.".format(self.name, kernel))
        debug("{}: Initrd   : {}.".format(self.name, ", ".join(initrd_files)))
        debug("{}: cmdline  : {}.".format(self.name, cmdline_input))
        debug("{}: osrelease: {}.".format(self.name, osrelease_file))
        debug("{}: efistub  : {}.".format(self.name, efistub))

        self._validate_files(location, kernel, *initrd_files, osrelease_file, efistub)
        with tempfile.TemporaryDirectory() as tmp:
            initrd = _create_initrd(tmp, *initrd_files)
            cmdline = _create_cmdline_file(tmp, cmdline_input)

            run(
                self._binary(Binaries.OBJCOPY),
                "--add-section",
                ".osrel={}".format(osrelease_file),
                "--change-section-vma",
                ".osrel=0x20000",
                "--add-section",
                ".cmdline={}".format(cmdline),
                "--change-section-vma",
                ".cmdline=0x30000",
                "--add-section",
                ".linux={}".format(kernel),
                "--change-section-vma",
                ".linux=0x40000",
                "--add-section",
                ".initrd={}".format(initrd),
                "--change-section-vma",
                ".initrd=0x3000000",
                efistub,
                output,
            )

            os.remove(initrd)
            os.remove(cmdline)
