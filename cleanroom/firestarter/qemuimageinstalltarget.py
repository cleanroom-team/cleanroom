#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Firestarter: qemu_image install command

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.firestarter.installtarget import InstallTarget
import cleanroom.firestarter.qemutools as qemu_tool
import cleanroom.firestarter.tools as tool
import cleanroom.helper.disk as disk
import cleanroom.helper.mount as mount
from cleanroom.helper.run import run
from cleanroom.printer import debug, verbose, trace

import os
from shutil import copyfile, copytree
import typing


def _create_hdd_image(device: disk.Device):
    verbose("hdd.img created.")
    partitioner = disk.Partitioner(device)

    partitioner.repartition(
        [
            disk.Partitioner.efi_partition(size=disk.byte_size("512M")),
            disk.Partitioner.swap_partition(size=disk.byte_size("1G"), name="swap"),
            disk.Partitioner.data_partition(name="data"),
        ]
    )

    verbose("hdd.img repartitioned.")

    debug("Format EFI partitition.")
    run("/usr/bin/mkfs.vfat", "-F32", device.device(1))
    debug("Set up swap partitition.")
    run("/usr/bin/mkswap", device.device(2))
    debug("Format data partitition.")
    run("/usr/bin/mkfs.btrfs", "-L", "fs_btrfs", device.device(3))


def _setup_btrfs(mount_point: str):
    trace("Creating subvolumes.")
    run("btrfs", "subvol", "create", "@btrfs", work_directory=mount_point)
    run("btrfs", "subvol", "create", "@home", work_directory=mount_point)
    run("btrfs", "subvol", "create", "@var", work_directory=mount_point)
    run("btrfs", "subvol", "create", ".images", work_directory=mount_point)


def _copy_efi(src: str, dest: str) -> int:
    try:
        efi_path = os.path.join(dest, "EFI")
        os.makedirs(efi_path, exist_ok=True)

        trace("Copying bootloader.")

        efi_src_path = os.path.join(src, "EFI")

        dirs = [
            d
            for d in os.listdir(efi_src_path)
            if os.path.isdir(os.path.join(efi_src_path, d))
        ]
        for d in dirs:
            dest = os.path.join(efi_path, d)
            trace("Copying {} to {}".format(os.path.join(efi_src_path, d), dest))
            copytree(
                os.path.join(efi_src_path, d), dest, dirs_exist_ok=True,
            )

        copytree(
            os.path.join(src, "loader"),
            os.path.join(dest, "loader"),
            dirs_exist_ok=True,
        )

    except Exception as e:
        debug("Failed to install EFI: {}.".format(e))
        return 1
    else:
        debug("Successfully installed EFI")
        return 0


def create_qemu_image(
    image_path: str,
    *,
    image_size: int,
    image_format: str = "qcow2",
    system_image_file: str,
    tmp_dir: str,
) -> str:
    trace("Creating image file {}.".format(image_path))
    with disk.NbdDevice.new_image_file(
        image_path, image_size, disk_format=image_format
    ) as device:
        _create_hdd_image(device)

        debug("mounting data partition for further setup.")
        with mount.Mount(
            device.device(3),
            os.path.join(tmp_dir, "data"),
            fs_type="btrfs",
            options="subvolid=0",
            fallback_cwd=os.getcwd(),
        ) as data_dir:
            _setup_btrfs(data_dir)

            trace("Copying image file")
            copyfile(
                system_image_file,
                os.path.join(data_dir, ".images", os.path.basename(system_image_file)),
            )

            with mount.Mount(
                device.device(1),
                os.path.join(tmp_dir, "efi_dest"),
                options="defaults",
                fs_type="vfat",
            ) as efi_dest_mnt:
                tool.execute_with_system_mounted(
                    lambda e, _: _copy_efi(e, efi_dest_mnt,),
                    image_file=system_image_file,
                    tmp_dir=tmp_dir,
                )

    return image_path


class QemuImageInstallTarget(InstallTarget):
    def __init__(self) -> None:
        super().__init__("qemu-image", "Set up hdd image and start it in qemu")

    def __call__(
        self, *, parse_result: typing.Any, tmp_dir: str, image_file: str
    ) -> int:
        image_path = create_qemu_image(
            os.path.join(tmp_dir, "hdd.img"),
            image_size=parse_result.hdd_size,
            image_format=parse_result.hdd_format,
            system_image_file=image_file,
            tmp_dir=tmp_dir,
        )

        return qemu_tool.run_qemu(
            parse_result,
            drives=["{}:{}".format(image_path, parse_result.hdd_format)],
            work_directory=tmp_dir,
        )

    def setup_subparser(self, subparser: typing.Any) -> None:
        qemu_tool.setup_parser_for_qemu(subparser)

        subparser.add_argument(
            "--hdd-size",
            dest="hdd_size",
            action="store",
            nargs="?",
            default="10G",
            help="Size of HDD to generate.",
        )

        subparser.add_argument(
            "--hdd-format",
            dest="hdd_format",
            action="store",
            nargs="?",
            default="qcow2",
            help="Format of HDD to generate.",
        )
