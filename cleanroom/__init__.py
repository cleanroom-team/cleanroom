#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

__all__ = ['Generator']

from . import parser

import os
import os.path
import sys

def checkForBinary(binary):
    if os.access(binary, os.X_OK):
        return binary
    else:
        return ''


class Generator:
    def __init__(self, work_dir, printer):
        self._parsers = []
        self._work_dir = work_dir
        self._pr = printer
        self._binaries = {}

        self.preflightTest();

    def addSystem(self, system):
        self._pr.trace('adding system {} to Generator.'.format(system))
        self._parsers = parser.Parser(self, system, self._pr)

    def generate(self):
        pass

    def preflightTest(self):
        self._binaries['ostree'] = checkForBinary('/usr/bin/ostree')
        self._binaries['rofiles-fuse'] = checkForBinary('/usr/bin/rofiles-fuse')
        self._binaries['foobar'] = checkForBinary('/usr/bin/foobar')

        passed = True
        for b in self._binaries.items():
            if b[1]:
                self._pr.verbose('{} found: {}...'.format(b[0], b[1]))
            else:
                self._pr.print('{} not found.'.format(b[0]))
                passed = False

        if not passed:
            sys.exit(1)


if __name__ == '__main__':
    pass
