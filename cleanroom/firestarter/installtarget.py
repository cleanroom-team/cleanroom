#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Firestarter InstallTarget class.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import typing


class InstallTarget(object):
    def __init__(self, name: str, help_string: str) -> None:
        self._name = name
        self._help_string = help_string

    def __call__(
        self, *, parse_result: typing.Any, tmp_dir: str, image_file: str
    ) -> int:
        assert False

    def setup_subparser(self, subparser: typing.Any) -> None:
        assert False

    @property
    def help_string(self) -> str:
        return self._help_string

    @property
    def name(self) -> str:
        return self._name
