#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""image_partition install target

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.firestarter.installtarget import InstallTarget
import cleanroom.firestarter.tools as tool
import cleanroom.helper.mount as mount

import os.path
from tempfile import TemporaryDirectory
from sys import exit
import typing


class ImagePartitionInstallTarget(InstallTarget):
    def __init__(self) -> None:
        super().__init__(
            "image_partition", "export image into image_partition and update EFI."
        )

    def setup_subparser(self, parser: typing.Any) -> None:
        parser.add_argument(
            "--efi-device",
            action="store",
            default="",
            dest="efi_device",
            help="The device containing the EFI partition.",
        )
        parser.add_argument(
            "--efi-options",
            action="store",
            default="",
            dest="efi_options",
            help="The mount options for the EFI partition.",
        )
        parser.add_argument(
            "--efi-fs-type",
            action="store",
            default="vfat",
            dest="efi_fs_type",
            help="The filesystem used on the EFI partition.",
        )


        parser.add_argument(
            "--image-device",
            action="store",
            default="",
            dest="image_device",
            help="The device containing the images.",
        )
        parser.add_argument(
            "--image-fs-type",
            action="store",
            default="btrfs",
            dest="image_fs_type",
            help="The filesystem type containing the image " "[defaults to btrfs].",
        )
        parser.add_argument(
            "--image-options",
            action="store",
            default="subvol=/.images",
            dest="image_options",
            help="Options used to mount image filessystem "
            "[defaults to: subvol=/.images]",
        )

    def __call__(self, parse_result: typing.Any) -> None:
        if not parse_result.efi_device:
            print("No --efi-device provided, stopping.")
            exit(1)
        if not parse_result.image_device:
            print("No --image-device provided, stopping.")
            exit(1)

        with TemporaryDirectory() as tempdir:
            with mount.Mount(
                parse_result.image_device,
                os.path.join(tempdir, "images"),
                options=parse_result.image_options,
                fs_type=parse_result.image_fs_type,
            ) as images_mnt:
                exported_file = tool.export_into_directory(
                    parse_result.system_name,
                    images_mnt,
                    version=parse_result.system_version,
                    repository=parse_result.repository,
                )

                tool.copy_efi_partition(
                    image_file=exported_file,
                    efi_device=parse_result.efi_device,
                    efi_options=parse_result.efi_options,
                    efi_fs_type=parse_result.efi_fs_type,
                    tempdir=tempdir,
                )
