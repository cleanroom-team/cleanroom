#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Container-as-basic-filesystem installation target

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.firestarter.installtarget import InstallTarget
import cleanroom.firestarter.tools as tool
from cleanroom.helper.btrfs import BtrfsHelper

import os
import typing


def _tar(efifs: str, rootfs: str, *, tarball_name: str, efi_tarball_name: str) -> None:

    # Extract data
    if efi_tarball_name:
        tool.run(
            "/usr/bin/bash",
            "-c",
            '( cd {} ; tar -cf "{}" --auto-compress .) '.format(
                efifs, efi_tarball_name
            ),
        )
    if tarball_name:
        tool.run(
            "/usr/bin/bash",
            "-c",
            '( cd {} ; tar -cf "{}" --auto-compress .) '.format(rootfs, tarball_name),
        )


class TarballInstallTarget(InstallTarget):
    def __init__(self) -> None:
        super().__init__("tarball", "Creates a tarball from the system image.")

    def setup_subparser(self, parser: typing.Any) -> None:
        parser.add_argument(
            "--efi-tarball",
            action="store",
            dest="efi_tarball",
            help="The tarball containing the EFI partition. [Default: empty -- skip]",
        )

        parser.add_argument(
            "--tarball",
            action="store",
            dest="tarball",
            help="The tarball containing the root filesystem image [Default: empty -- skip].",
        )

    def __call__(self, parse_result: typing.Any) -> None:
        if not parse_result.tarball and not parse_result.efi_tarball:
            return

        # Mount filessytems and copy the rootfs into import_dir:
        tool.execute_with_system_mounted(
            lambda e, r: _tar(
                e,
                r,
                tarball_name=parse_result.tarball,
                efi_tarball_name=parse_result.efi_tarball,
            ),
            repository=parse_result.repository,
            system_name=parse_result.system_name,
            system_version=parse_result.system_version,
        )
