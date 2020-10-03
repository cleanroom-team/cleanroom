"""clr_kernel command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import shutil
import typing
import os.path


def move_kernel(system_context: SystemContext, variant: str) -> str:
    vmlinuz = os.path.join(system_context.boot_directory, "vmlinuz")

    default_file = system_context.file_name(f"/usr/lib/kernel/default-{variant}")
    installed_kernel = os.path.join("/usr/lib/kernel", os.readlink(default_file))
    os.remove(default_file)

    prefix = f"org.clearlinux.{variant}."
    version = os.path.basename(installed_kernel)[len(prefix) :]

    shutil.copyfile(system_context.file_name(installed_kernel), vmlinuz)

    return version


def update_cmdline(system_context: SystemContext, version: str, variant: str):
    with open(
        system_context.file_name(f"/usr/lib/kernel/cmdline-{version}.{variant}"), "r"
    ) as cmd:
        clr_cmdline = [a.strip() for a in cmd.read().split("\n") if a and a != "quiet"]

    in_cmdline = [
        a for a in system_context.substitution("KERNEL_CMDLINE", "").split(" ") if a
    ]

    cmdline = [
        *in_cmdline,
        *clr_cmdline,
    ]
    cmdline_str = " ".join([a for a in cmdline if a])

    system_context.set_substitution("KERNEL_CMDLINE", cmdline_str)


def move_initrds(system_context: SystemContext):
    initrd_parts = os.path.join(system_context.boot_directory, "initrd-parts")
    os.makedirs(initrd_parts, exist_ok=True)

    i915 = os.path.join(initrd_parts, "05-i915.cpio.xz")
    shutil.move(
        system_context.file_name("/usr/lib/initrd.d/00-intel-ucode.cpio"),
        os.path.join(initrd_parts, "00-intel-ucode.cpio"),
    )
    shutil.move(
        system_context.file_name("/usr/lib/initrd.d/i915-firmware.cpio.xz"), i915
    )

    run("/usr/bin/xz", "-d", i915)

    os.rmdir(system_context.file_name("/usr/lib/initrd.d"))


class ClrKernelCommand(Command):
    """The clr_kernel command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "clr_kernel",
            syntax_string="[variant=(native)]",
            help_string="Set up a Kernel. If no variant is given, then the default kernel is installed.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_no_args(location, *args)
        self._validate_kwargs(location, ("variant",), **kwargs)
        self._require_kwargs(location, ("variant",), **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""

        variant = kwargs.get("variant", "native")
        kernel = f"kernel-{variant}"

        self._execute(
            location, system_context, "swupd", kernel,
        )

        version = move_kernel(system_context, variant)
        update_cmdline(system_context, version, variant)

        move_initrds(system_context)
