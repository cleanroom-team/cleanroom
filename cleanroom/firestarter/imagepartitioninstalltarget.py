#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CleanRoom binary.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.firestarter.installtarget import InstallTarget
import cleanroom.firestarter.tools as tool
import cleanroom.helper.mount as mount

import os.path
from tempfile import TemporaryDirectory
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
            default="/dev/sda1",
            dest="efi_device",
            help="The device containing the EFI partition.",
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
                    tempdir=tempdir,
                )
