#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""image_partition install target

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.firestarter.installtarget import InstallTarget
import cleanroom.firestarter.tools as tool
import cleanroom.helper.mount as mount
from cleanroom.printer import debug, trace

import os
from shutil import copy2, copytree
from sys import exit
import typing


def _copy_file(src: str, dest: str, overwrite: bool):
    file = os.path.basename(src)
    if not os.path.exists(os.path.join(dest, file)) or overwrite:
        debug(
            "Copying {} into {}{}".format(src, dest, " [FORCE]." if overwrite else ".")
        )
        copy2(src, dest)
    else:
        debug("Skipped copy of {} into {}.".format(src, dest))


def _copy_efi(
    src: str, dest: str, *, include_bootloader: bool = False, overwrite: bool = False
) -> int:
    try:
        efi_path = os.path.join(dest, "EFI")
        os.makedirs(efi_path, exist_ok=True)

        linux_src_path = os.path.join(src, "EFI/Linux")
        kernels = [
            f
            for f in os.listdir(linux_src_path)
            if os.path.isfile(os.path.join(linux_src_path, f))
        ]
        debug('Found kernel(s): "{}".'.format('", "'.join(kernels)))
        assert len(kernels) == 1
        kernel = kernels[0]

        _copy_file(
            os.path.join(linux_src_path, kernel),
            os.path.join(dest, "EFI/Linux"),
            overwrite=overwrite,
        )

        if include_bootloader:
            trace("Copying bootloader.")

            efi_src_path = os.path.join(src, "EFI")

            dirs = [
                d
                for d in os.listdir(efi_src_path)
                if d != "Linux" and os.path.isdir(os.path.join(efi_src_path, d))
            ]
            for d in dirs:
                trace(
                    "Copying {} to {}".format(os.path.join(efi_src_path, d), efi_path)
                )
                copytree(os.path.join(efi_src_path, d), efi_path, dirs_exist_ok=True)

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


class ImagePartitionInstallTarget(InstallTarget):
    def __init__(self) -> None:
        super().__init__(
            "image_partition", "export image into image_partition and update EFI."
        )

    def setup_subparser(self, subparser: typing.Any) -> None:
        subparser.add_argument(
            "--efi-device",
            action="store",
            default="",
            dest="efi_device",
            help="The device containing the EFI partition.",
        )
        subparser.add_argument(
            "--efi-options",
            action="store",
            default="",
            dest="efi_options",
            help="The mount options for the EFI partition.",
        )
        subparser.add_argument(
            "--efi-fs-type",
            action="store",
            default="vfat",
            dest="efi_fs_type",
            help="The filesystem used on the EFI partition.",
        )

        subparser.add_argument(
            "--image-device",
            action="store",
            default="",
            dest="image_device",
            help="The device containing the images.",
        )
        subparser.add_argument(
            "--image-fs-type",
            action="store",
            default="btrfs",
            dest="image_fs_type",
            help="The filesystem type containing the image " "[defaults to btrfs].",
        )
        subparser.add_argument(
            "--image-options",
            action="store",
            default="subvol=/.images",
            dest="image_options",
            help="Options used to mount image filessystem "
            "[defaults to: subvol=/.images]",
        )
        subparser.add_argument(
            "--add-bootloader",
            action="store_true",
            default=False,
            dest="include_bootloader",
            help="Install the boot loader files in addition to the kernel.",
        )
        subparser.add_argument(
            "--overwrite",
            action="store_true",
            default=False,
            dest="overwrite",
            help="Overwrite existing images/kernels.",
        )

    def __call__(
        self, *, parse_result: typing.Any, tmp_dir: str, image_file: str
    ) -> int:
        if not parse_result.efi_device:
            print("No --efi-device provided, stopping.")
            exit(1)
        if not parse_result.image_device:
            print("No --image-device provided, stopping.")
            exit(1)

        with mount.Mount(
            parse_result.image_device,
            os.path.join(tmp_dir, "images"),
            options=parse_result.image_options,
            fs_type=parse_result.image_fs_type,
        ) as images_mnt:
            _copy_file(image_file, images_mnt, overwrite=parse_result.overwrite)

        with mount.Mount(
            parse_result.efi_device,
            os.path.join(tmp_dir, "efi_dest"),
            options=parse_result.efi_options,
            fs_type=parse_result.efi_fs_type,
        ) as efi_dest_mnt:
            return tool.execute_with_system_mounted(
                lambda e, _: _copy_efi(
                    e,
                    efi_dest_mnt,
                    include_bootloader=parse_result.include_bootloader,
                    overwrite=parse_result.overwrite,
                ),
                image_file=image_file,
                tmp_dir=tmp_dir,
            )
