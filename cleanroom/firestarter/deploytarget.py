#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generic deployment target

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.firestarter.installtarget import InstallTarget

import typing


class DeployInstallTarget(InstallTarget):
    def __init__(self) -> None:
        super().__init__(
            "deploy", "Deploy the machine as specified in its deployment information"
        )

    def setup_subparser(self, subparser: typing.Any) -> None:
        pass

    def __call__(
        self, *, parse_result: typing.Any, tmp_dir: str, image_file: str
    ) -> int:
        return 0
