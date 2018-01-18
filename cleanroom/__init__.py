#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

__all__ = ['Generator']

from . import parser

import os
import os.path


class PreflightError(RuntimeError):
    pass


def checkForBinary(binary):
    if os.access(binary, os.X_OK):
        return binary
    else:
        return ''


class Context:
    def __init__(self, system_dir, work_dir, printer):
        self._system_dir = system_dir
        self._work_dir = work_dir
        self._printer = printer
        self._binaries = {
            'ostree': checkForBinary('/usr/bin/ostree'),
            'rofiles-fuse': checkForBinary('/usr/bin/rofiles-fuse')
        }
        self.generator = None

    def printer(self):
        return self._printer

    def workDirectory(self):
        return self._workDir

    def systemsDirectory(self):
        return self._systemDir

    def systemsCleanRoomDirectory(self):
        return os.path.join(systemsDirectory(), 'cleanroom')

    def systemsCommandsDirectory(self):
        return os.path.join(systemsCleanRoomDirectory(), 'commands')


    def priflightCheck(self):
        self._printer.h1('Running Preflight Checks.')

        binaries = self._preflightBinaries()
        users = self._preflightUsers()

        if not binaries or not users:
            raise PreflightError()

    def _preflightBinaries(self):
        ''' Check executables '''
        passed = True
        for b in self._binaries.items():
            if b[1]:
                self._printer.info('{} found: {}...'.format(b[0], b[1]))
            else:
                self._printer.warn('{} not found.'.format(b[0]))
                passed = False
        return passed

    def _preflightUsers(self):
        ''' Check tha the script is running as root '''
        if os.geteuid() == 0:
            self._printer.verbose('Running as root.')
            return True
        self._printer.warn('Not running as root.')
        return False


class Generator:
    def __init__(self, system_dir, work_dir, printer):
        self._context = Context(system_dir, work_dir, printer)
        self._context.generator = self

    def prepare(self):
        pass

    def generate(self):
        pass


if __name__ == '__main__':
    pass
