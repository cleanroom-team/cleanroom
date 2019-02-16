#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Firestarter: Simple qemu runner

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.firestarter.installtarget import InstallTarget
import cleanroom.firestarter.tools as tool
import cleanroom.firestarter.qemutools as qemu_tool

import os.path
from tempfile import TemporaryDirectory
import typing


class QemuBootInstallTarget(InstallTarget):
    def __init__(self) -> None:
        super().__init__('qemu_boot', 'Boot image in qemu')

    def __call__(self, parse_result: typing.Any) -> None:
        with TemporaryDirectory(prefix='clrm_qemu_') as tempdir:
            extracted_version \
                    = tool.write_image(parse_result.system_name, tempdir,
                                       repository=parse_result.repository,
                                       version=parse_result.system_version)

            extracted_image = os.path.join(tempdir,
                                           'clrm_{}'.format(extracted_version))
            assert os.path.isfile(extracted_image)

            qemu_tool.run_qemu(parse_result,
                               drives=['{}:raw'.format(extracted_image)],
                               work_directory=tempdir)

    def setup_subparser(self, parser: typing.Any) -> None:
        qemu_tool.setup_parser_for_qemu(parser)
