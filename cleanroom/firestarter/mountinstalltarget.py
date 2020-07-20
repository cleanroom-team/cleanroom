#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mount an exported system

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.firestarter.installtarget import InstallTarget
import cleanroom.firestarter.tools as tool
from cleanroom.printer import verbose

import os
from shlex import split
import typing


def _execution(efi: str, rootfs: str, *, command: str) -> int:
    to_exec = command or '/usr/bin/bash -c "read -n1 -s"'
    prompt = "" if command else "<<< Press any key to continue >>>"

    env = os.environ
    env["EFI_MOUNT"] = efi
    env["ROOT_MOUNT"] = rootfs

    verbose("Running {}.".format(command))
    verbose('EFI_MOUNT env var set to : "{}".'.format(efi))
    verbose('ROOT_MOUNT env var set to: "{}".'.format(rootfs))

    print('EFI partition is mounted at "{}".'.format(efi))
    print('Root partition is mounted at "{}".'.format(rootfs))

    if prompt:
        print(prompt)

    return tool.run(*split(to_exec), env=env).returncode


class MountInstallTarget(InstallTarget):
    def __init__(self) -> None:
        super().__init__(
            "mount",
            "RO mounts EFI and root partition till "
            "the given command is done executing.",
        )

    def __call__(
        self, *, parse_result: typing.Any, tmp_dir: str, image_file: str
    ) -> int:
        return tool.execute_with_system_mounted(
            lambda e, r: _execution(e, r, command=parse_result.command),
            image_file=image_file,
            tmp_dir=tmp_dir,
        )

    def setup_subparser(self, subparser: typing.Any) -> None:
        subparser.add_argument(
            "--command",
            action="store",
            nargs="?",
            default="",
            help="Command to run once mounted " "[default: wait for keypress].",
        )
