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
from tempfile import TemporaryDirectory
import typing


def _execution(efi: str, rootfs: str, *, command: str) -> None:
    to_exec = command or '/usr/bin/bash -c "read -n1 -s"'
    prompt = '' if command else \
        '<<< Press any key to continue >>>'

    env = os.environ
    env['EFI_MOUNT'] = efi
    env['ROOT_MOUNT'] = rootfs

    verbose('Running {}.'.format(command))
    verbose('EFI_MOUNT env var set to : "{}".'.format(efi))
    verbose('ROOT_MOUNT env var set to: "{}".'.format(rootfs))

    print('EFI partition is mounted at "{}".'.format(efi))
    print('Root partition is mounted at "{}".'.format(rootfs))

    if prompt:
        print(prompt)

    tool.run(*split(to_exec), env=env)


class MountInstallTarget(InstallTarget):
    def __init__(self) -> None:
        super().__init__('mount',
                         'RO mounts EFI and root partition till '
                         'the given command is done executing.')

    def __call__(self, parse_result: typing.Any) -> None:
        tool.execute_with_system_mounted(
            lambda e, r: _execution(e, r, command=parse_result.command),
            repository=parse_result.repository,
            system_name=parse_result.system_name,
            system_version=parse_result.system_version)

    def setup_subparser(self, parser: typing.Any) -> None:
        parser.add_argument('--command', action='store', nargs='?',
                            default='', help='Command to run once mounted '
                                             '[default: wait for keypress].')
