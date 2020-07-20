#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Container-as-basic-filesystem installation target

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.firestarter.installtarget import InstallTarget
import cleanroom.firestarter.tools as tool

import os
import typing


def _tar(efi_fs: str, rootfs: str, *, tarball_name: str, efi_tarball_name: str) -> int:

    # Extract data
    result = 0
    if efi_tarball_name:
        result = tool.run(
            "/usr/bin/bash",
            "-c",
            '( cd {} ; tar -cf "{}" --auto-compress .) '.format(
                efi_fs, efi_tarball_name
            ),
        ).returncode
    if tarball_name:
        result += tool.run(
            "/usr/bin/bash",
            "-c",
            '( cd {} ; tar -cf "{}" --auto-compress .) '.format(rootfs, tarball_name),
        ).returncode

    return result


class TarballInstallTarget(InstallTarget):
    def __init__(self) -> None:
        super().__init__("tarball", "Creates a tarball from the system image.")

    def setup_subparser(self, subparser: typing.Any) -> None:
        subparser.add_argument(
            "--efi-tarball",
            action="store",
            dest="efi_tarball",
            help="The tarball containing the EFI partition. [Default: empty -- skip]",
        )

        subparser.add_argument(
            "--tarball",
            action="store",
            dest="tarball",
            help="The tarball containing the root filesystem image [Default: empty -- skip].",
        )

    def __call__(
        self, *, parse_result: typing.Any, tmp_dir: str, image_file: str
    ) -> int:
        if not parse_result.tarball and not parse_result.efi_tarball:
            return 1

        assert os.path.isfile(image_file)

        # Mount filessystems and copy the rootfs into import_dir:
        return tool.execute_with_system_mounted(
            lambda e, r: _tar(
                e,
                r,
                tarball_name=parse_result.tarball,
                efi_tarball_name=parse_result.efi_tarball,
            ),
            image_file=image_file,
            tmp_dir=tmp_dir,
        )
