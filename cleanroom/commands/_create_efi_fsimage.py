# -*- coding: utf-8 -*-
"""_create_efi_fsimage command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from tempfile import TemporaryDirectory
from cleanroom.exceptions import GenerateError
from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.helper.file import file_size
from cleanroom.helper.disk import mib_ify
from cleanroom.helper.run import run
from cleanroom.systemcontext import SystemContext
from cleanroom.printer import trace, verbose


import shutil
import typing
import os


mib = 1024 * 1024


def _copy_efi_file(source: str, destination: str) -> None:
    if os.path.isdir(destination):
        file_name = os.path.basename(source)
        destination = os.path.join(destination, file_name)
    else:
        dest_dir = os.path.dirname(destination)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

    shutil.copyfile(source, destination)
    os.chmod(destination, 0o755)


def _get_tree_size(start_path: str) -> int:
    total_size = 0
    for dirpath, _, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


def _minimum_efi_size(kernel_size: int) -> int:
    return mib_ify(int(kernel_size * 1.05)) * mib


def _calculate_efi_size(min_efi_size: int, efi_size: int) -> int:
    if efi_size > 0:
        assert min_efi_size < efi_size
        return mib_ify(efi_size) * mib  # rounded to full MiB
    return _minimum_efi_size(min_efi_size)


def _populate_with_efi_emulator(staging_area: str, efi_emulator: str):
    verbose("Installing Clover binaries into EFI partition")
    assert efi_emulator, "Missing EFI emulator path"

    shutil.copy(
        os.path.join(efi_emulator, "Bootloaders/x64/boot7"),
        os.path.join(staging_area, "boot"),
        follow_symlinks=False,
    )
    efi_dir = os.path.join(staging_area, "EFI")
    if not os.path.isdir(efi_dir):
        os.makedirs(efi_dir)
    shutil.copytree(
        os.path.join(efi_emulator, "EFI/CLOVER"), os.path.join(efi_dir, "CLOVER")
    )

    config_file = os.path.join(efi_dir, "CLOVER/config.plist")
    with open(config_file, "wb") as config:
        config.write(
            """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Boot</key>
	<dict>
		<key>DefaultVolume</key>
		<string>EFI</string>
		<key>DefaultLoader</key>
		<string>\\EFI\\systemd\\systemd-bootx64.efi</string>
		<key>Fast</key>
		<true/>
	</dict>
	<key>GUI</key>
	<dict>
		<key>Custom</key>
		<dict>
			<key>Entries</key>
			<array>
				<dict>
					<key>Hidden</key>
					<false/>
					<key>Disabled</key>
					<false/>
					<key>Image</key>
					<string>os_arch</string>
					<key>Volume</key>
					<string>EFI</string>
					<key>Path</key>
					<string>\\EFI\\systemd\\systemd-bootx64.efi</string>
					<key>Title</key>
					<string>Cleanroom Linux</string>
					<key>Type</key>
					<string>Linux</string>
				</dict>
			</array>
		</dict>
	</dict>
</dict>
</plist>
""".encode("utf-8")
        )


def _copy_staging_area_into_efi_partition_file(
    staging_area: str, efi_file: str, *, mmd: str, mcopy: str
):
    trace(f"Staging area: staging: {staging_area}, EFI file: {efi_file}).")

    for root, dirs, files in os.walk(staging_area):
        trace(f"    root: {root}.")

        relative_path = os.path.relpath(root, start=staging_area)
        for d in dirs:
            trace(f"        dir: {d}.")
            run(mmd, "-i", efi_file, f"::{os.path.join(relative_path, d)}")
        for f in files:
            trace(f"        file: {f}.")
            run(mcopy, "-i", efi_file, os.path.join(root, f), f"::{relative_path}")


class CreateEfiFsimageCommand(Command):
    """The _create_efi_fsimage Command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_create_efi_fsimage",
            syntax="EFI_IMAGE_FILE "
            "[kernel_file=<KERNEL_FILE>] "
            "[systemd_boot_loader=<BOOTLOADER> "
            "[extra_files=<EXTRA_FILE_DIR>] "
            "[efi_emulator=<EMULATOR_DIR> "
            "[requested_size=<SIZE>] "
            "[partition_label=<STRING>] "
            "[root_hash=<ROOT_HASH>]",
            help_string="Export a filesystem image.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate arguments."""
        self._validate_args_exact(
            location, 1, "{} needs a filename for the kernel.", *args
        )
        self._validate_kwargs(
            location,
            (
                "systemd_boot_loader",
                "extra_files",
                "efi_emulator",
                "kernel_file",
                "partition_label",
                "requested_size",
                "root_hash",
            ),
            **kwargs,
        )

    def _format_efi_partition(self, efi_file: str, *, partition_label: str = ""):
        mkfs_args: typing.List[str] = [
            self._binary(Binaries.MKFS_VFAT),
        ]
        if partition_label:
            mkfs_args += [
                "-n",
                partition_label,
            ]
        mkfs_args += [efi_file]
        run(*mkfs_args)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        efi_file = args[0]

        kernel_file = kwargs.get("kernel_file", "")
        boot_loader_file = kwargs.get("systemd_boot_loader", "")
        requested_size = int(kwargs.get("requested_size", "0"))
        extra_files = kwargs.get("extra_files", "")
        efi_emulator = kwargs.get("efi_emulator", "")
        partition_label = kwargs.get("partition_label", "")
        root_hash = kwargs.get("root_hash", "")

        if kernel_file:
            if not os.path.isfile(boot_loader_file):
                raise GenerateError(
                    "You must provide a boot loader file and that must be a file when passing a kernel file."
                )

        if extra_files:
            extra_files = os.path.join(
                system_context.systems_definition_directory, extra_files
            )
            if not os.path.isdir(extra_files):
                raise GenerateError(f"extra_files {extra_files} is not a directory.")

        kernel_size = file_size(None, kernel_file) if kernel_file else 256 * 1024
        boot_loader_size = file_size(None, boot_loader_file)

        min_efi_size = kernel_size
        if kernel_file:
            if efi_emulator:
                min_efi_size += 10 * mib
            if extra_files:
                min_efi_size += _get_tree_size(extra_files)
            min_efi_size += 2 * boot_loader_size

        efi_size = _calculate_efi_size(min_efi_size, requested_size)

        # create file:
        with open(efi_file, "wb") as fd:
            fd.seek(efi_size - 1)
            fd.write(b"\0")

        # format file:
        self._format_efi_partition(efi_file, partition_label=partition_label)

        with TemporaryDirectory() as staging_area:
            if kernel_file:
                if efi_emulator:
                    _populate_with_efi_emulator(staging_area, efi_emulator)
                    trace("... Clover binaries have been installed.")

                if extra_files:
                    shutil.copytree(extra_files, staging_area, dirs_exist_ok=True)
                    trace("... Extra EFI files installed.")

                # install systemd as default boot loader:
                default_boot_path = os.path.join(staging_area, "EFI/Boot")
                os.makedirs(default_boot_path)
                trace('... "EFI/boot" directory created.')
                _copy_efi_file(
                    boot_loader_file, os.path.join(default_boot_path, "BOOTX64.EFI")
                )
                trace("... default boot loader installed")

                os.makedirs(os.path.join(staging_area, "EFI/systemd"))
                trace('... "EFI/systemd" directory created.')
                _copy_efi_file(
                    boot_loader_file,
                    os.path.join(staging_area, "EFI/systemd/systemd-bootx64.efi"),
                )
                trace("... systemd boot loader installed.")

                linux_dir = os.path.join(staging_area, "EFI/Linux")
                os.makedirs(linux_dir)
                trace('... "EFI/Linux" created.')
                _copy_efi_file(kernel_file, linux_dir)
                trace("... kernel installed")
            else:
                with open(os.path.join(staging_area, "no_boot.txt"), "w") as f:
                    f.write("No EFI boot support installed\n")

            if root_hash:
                with open(os.path.join(staging_area, "root_hash"), "w") as f:
                    f.write(f"{root_hash}")

            _copy_staging_area_into_efi_partition_file(
                staging_area,
                efi_file,
                mmd=self._binary(Binaries.MTOOLS_MMD),
                mcopy=self._binary(Binaries.MTOOLS_MCOPY),
            )
