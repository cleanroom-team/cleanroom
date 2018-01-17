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


def directoryMissingOrEmpty(directory):
    if os.path.isdir(directory):
        return True
    (dirpath, dirnames, files) = os.walk(directory)
    return len(dirnames) == 0 and len(files) == 0


class Generator:
    def __init__(self, system_dir, work_dir, printer):
        self._pr = printer
        self._parsers = []
        self._systemDir = system_dir
        self._workDir =  work_dir
        self._binaries = {
            'ostree': checkForBinary('/usr/bin/ostree'),
            'rofiles-fuse': checkForBinary('/usr/bin/rofiles-fuse')
        }

        self.preflightTest()

    def workDirectory(self):
        return self._workDir

    def addSystem(self, system):
        self._pr.trace('adding system {} to Generator.'.format(system))
        self._parsers = parser.Parser(self, system, self._pr)

    def prepare(self):
        pass       

    def generate(self):
        pass

    def preflightTest(self):
        self._pr.h1('Running Preflight Checks.')

        binaries = self._preflightBinaries()
        users = self._preflightUsers()
        directories = self._preflightDirectories()

        if not binaries or not users or not directories:
            sys.exit(1)

    def _preflightBinaries(self):
        ''' Check executables '''
        passed = True
        for b in self._binaries.items():
            if b[1]:
                self._pr.info('{} found: {}...'.format(b[0], b[1]))
            else:
                self._pr.error('{} not found.'.format(b[0]))
                passed = False
        return passed

    def _preflightUsers(self):
        ''' Check tha the script is running as root '''
        if os.geteuid() == 0:
            self._pr.verbose('Running as root.')
            return True
        self._pr.error('Not running as root.')
        return False

    def _preflightDirectories(self):
        pass


if __name__ == '__main__':
    pass
