"""clr_kernel command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import glob
import shutil
import typing
import os


def move_kernel(system_context: SystemContext, variant: str) -> str:
    vmlinuz = os.path.join(system_context.boot_directory, "vmlinuz")

    default_file = system_context.file_name(f"/usr/lib/kernel/default-{variant}")
    installed_kernel = os.path.join("/usr/lib/kernel", os.readlink(default_file))
    os.remove(default_file)

    prefix = f"org.clearlinux.{variant}."
    kernel_version = os.path.basename(installed_kernel)[len(prefix) :]

    shutil.move(system_context.file_name(installed_kernel), vmlinuz)

    return kernel_version


def update_cmdline(system_context: SystemContext, version: str, variant: str):
    cmdline_file = system_context.file_name(
        f"/usr/lib/kernel/cmdline-{version}.{variant}"
    )
    with open(cmdline_file, "r") as cmd:
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

    os.remove(cmdline_file)


def move_initrds(system_context: SystemContext, *, variant: str, kernel_version: str):
    initrd_parts = system_context.initrd_parts_directory
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

    main = os.path.join(initrd_parts, "50-clr.gz")
    shutil.move(
        system_context.file_name("/usr/lib/initrd.d/clr-init.cpio.gz"),
        main,
    )
    run(
        "/usr/bin/gzip",
        "-d",
        main,
    )

    os.rmdir(system_context.file_name("/usr/lib/initrd.d"))

    modules_initrd = system_context.file_name(
        f"/usr/lib/kernel/initrd-org.clearlinux.{variant}.{kernel_version}"
    )
    assert os.path.isfile(modules_initrd)
    shutil.move(modules_initrd, os.path.join(initrd_parts, "60-modules.xz"))
    run("/usr/bin/xz", "-d", os.path.join(initrd_parts, "60-modules.xz"))

    # Remove unnecessary files:
    for mid in glob.glob(
        system_context.file_name("/usr/lib/kernel/initrd-org.clearlinux.*")
    ):
        os.remove(mid)


class ClrKernelCommand(Command):
    """The clr_kernel command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "clr_kernel",
            syntax_string="[variant=(native)]",
            help_string="Set up a Kernel. If no variant is given, "
            "then the default kernel is installed.",
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

    def register_substitutions(self) -> typing.List[typing.Tuple[str, str, str]]:
        return [
            ("KERNEL_VERSION", "", "The version of the kernel being used"),
        ]

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
            location,
            system_context,
            "swupd",
            kernel,
            "boot-encrypted",
        )

        kernel_version = move_kernel(system_context, variant)
        update_cmdline(system_context, kernel_version, variant)

        system_context.set_substitution("KERNEL_VERSION", f"{kernel_version}.{variant}")
        move_initrds(system_context, kernel_version=kernel_version, variant=variant)

        # fix up permissions of some files that were just installed:
        os.chmod(
            system_context.file_name(
                "/usr/lib/systemd/system/blk-availability.service"
            ),
            0o644,
        )
        os.chmod(
            system_context.file_name("/usr/lib/systemd/system/dm-event.service"), 0o644
        )
        os.chmod(
            system_context.file_name("/usr/lib/systemd/system/dm-event.socket"), 0o644
        )
        os.chmod(
            system_context.file_name("/usr/lib/systemd/system/lvm2-lvmetad.service"),
            0o644,
        )
        os.chmod(
            system_context.file_name("/usr/lib/systemd/system/lvm2-lvmetad.socket"),
            0o644,
        )
        os.chmod(
            system_context.file_name("/usr/lib/systemd/system/lvm2-pvscan@.service"),
            0o644,
        )
