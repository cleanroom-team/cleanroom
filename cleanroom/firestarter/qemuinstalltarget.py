#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Firestarter: Simple qemu runner

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.firestarter.installtarget import InstallTarget
import cleanroom.firestarter.qemutools as qemu_tool

import os
import typing


class QemuInstallTarget(InstallTarget):
    def __init__(self) -> None:
        super().__init__("qemu", "Boot image in qemu")

    def __call__(
        self, *, parse_result: typing.Any, tmp_dir: str, image_file: str
    ) -> int:
        if not "DISPLAY" in os.environ:
            print("No DISPLAY variable set: Can not start qemu.")
            exit(1)

        clrm_device = "{}:raw:read-only".format(image_file)
        if parse_result.usb_clrm:
            clrm_device += ":usb"

        return qemu_tool.run_qemu(
            parse_result, drives=[clrm_device], work_directory=tmp_dir,
        )

    def setup_subparser(self, subparser: typing.Any) -> None:
        qemu_tool.setup_parser_for_qemu(subparser)
        subparser.add_argument(
            "--usb-clrm",
            dest="usb_clrm",
            action="store_true",
            help="Put CLRM onto a virtual USB stick",
        )
