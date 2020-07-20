#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Copy Install Target

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.firestarter.installtarget import InstallTarget

from shutil import copy
import typing


class CopyInstallTarget(InstallTarget):
    def __init__(self) -> None:
        super().__init__("copy", "copy the image to a directory, device or file")

    def setup_subparser(self, subparser: typing.Any) -> None:
        subparser.add_argument(
            dest="target", action="store", help="The target to copy into.",
        )

    def __call__(
        self, *, parse_result: typing.Any, tmp_dir: str, image_file: str
    ) -> int:
        assert parse_result.target

        copy(image_file, parse_result.target)

        return 0
