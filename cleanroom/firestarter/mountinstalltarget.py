#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mount an exported system

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.firestarter.installtarget import InstallTarget
import cleanroom.firestarter.tools as tool
import cleanroom.helper.mount as mount
import cleanroom.helper.disk as disk
from cleanroom.printer import verbose

import os
from shlex import split
from tempfile import TemporaryDirectory
import typing


class MountInstallTarget(InstallTarget):
    def __init__(self) -> None:
        super().__init__('mount',
                         'RO mounts EFI and root partition till '
                         'the given command is done executing.')

    def __call__(self, parse_result: typing.Any) -> None:
        with TemporaryDirectory(prefix='clrm_qemu_') as tempdir:
            image_path \
                = tool.export_into_directory(
                    parse_result.system_name, tempdir,
                    repository=parse_result.repository,
                    version=parse_result.system_version)

            assert os.path.isfile(image_path)

            with disk.NbdDevice(image_path, disk_format='raw') as device:
                with mount.Mount(device.device(1), os.path.join(tempdir, 'EFI'),
                                 fs_type='vfat', options='ro') as efi:
                    with mount.Mount(device.device(2),
                                     os.path.join(tempdir, 'root'),
                                     fs_type='squashfs', options='ro') as root:
                        command = parse_result.command \
                            or '/usr/bin/bash -c "read -n1 -s"'
                        prompt = '' if parse_result.command else \
                            '<<< Press any key to continue >>>'
                        env = os.environ

                        env['EFI_MOUNT'] = efi
                        env['ROOT_MOUNT'] = root

                        verbose('Running {}.'.format(command))
                        verbose('EFI_MOUNT env var set to : "{}".'.format(efi))
                        verbose('ROOT_MOUNT env var set to: "{}".'.format(root))

                        if prompt:
                            print(prompt)
                        tool.run(*split(command), env=env)

    def setup_subparser(self, parser: typing.Any) -> None:
        parser.add_argument('--command', action='store', nargs='?',
                            default='', help='Command to run once mounted '
                                             '[default: wait for keypress].')
