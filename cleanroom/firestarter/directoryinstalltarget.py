#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CleanRoom binary.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.firestarter.installtarget import InstallTarget
import cleanroom.firestarter.tools as tool

import typing


class DirectoryInstallTarget(InstallTarget):
    def __init__(self) -> None:
        super().__init__('directory', 'export image into directory')

    def setup_subparser(self, parser: typing.Any) -> None:
        parser.add_argument(dest='target_directory', action='store',
                            help='The directory to export into.')
        parser.add_argument('--mode', action='store', default=0, type=int,
                            help='mode of exported file.')
        parser.add_argument('--owner', action='store',
                            help='owner of exported file')
        parser.add_argument('--group', action='store',
                            help='group of exported file')

        parser.add_argument('--create-target-directory',
                            dest='create_directory',
                            action='store_true')

    def __call__(self, parse_result: typing.Any) -> None:
        tool.export_into_directory(parse_result.system_name,
                                   parse_result.target_directory,
                                   version=parse_result.system_version,
                                   repository=parse_result.repository,
                                   create_directory=parse_result
                                   .create_directory,
                                   owner=parse_result.owner,
                                   group=parse_result.group,
                                   mode=parse_result.mode)
