#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from . import exceptions
from . import parser
from . import printer
from . import generator

from enum import Enum, auto, unique
import os


@unique
class Binaries(Enum):
    OSTREE = auto()
    ROFILES_FUSE = auto()


def checkForBinary(binary):
    return binary if os.access(binary, os.X_OK) else ''


class Context:
    def Create(verbose = 0, ignore_errors = False):
        prt = printer.Printer(verbose)
        return Context(prt, ignore_errors)


    def __init__(self, printer, ignore_errors):
        self.printer = printer
        self.binaries = {
            Binaries.OSTREE: checkForBinary('/usr/bin/ostree'),
            Binaries.ROFILES_FUSE: checkForBinary('/usr/bin/rofiles-fuse')
        }
        self.generator = generator.Generator(self)

        self.ignore_errors = ignore_errors

        self._work_dir = None
        self._system_dir = None
        self._command_dir = None

        self._sys_cleanroom_dir = None
        self._sys_commands_dir = None

    def binary(self, selector):
        binary = self.binaries[selector]
        self.printer.trace('Getting binary for {}: {}.'.format(selector, binary))
        return binary

    def setDirectories(self, system_dir, work_dir):
        self.printer.verbose('Setting up Directories.')

        if self._system_dir != None:
            raise exceptions.ContextError('Directories were already set up.')

        # main directories:
        self._system_dir = system_dir
        self._work_dir = work_dir
        self._command_dir = os.path.join(os.path.dirname(__file__), 'commands')

        self._work_repo_dir = os.path.join(work_dir, 'repo')
        self._work_systems_dir = os.path.join(work_dir, 'systems')

        # setup secondary directories:
        self._sys_cleanroom_dir = os.path.join(self._system_dir, 'cleanroom')
        self._sys_commands_dir = os.path.join(self._sys_cleanroom_dir, 'commands')

        self.printer.info('Context: System dir       = "{}".'.format(self._system_dir))
        self.printer.info('Context: Work dir         = "{}".'.format(self._work_dir))
        self.printer.info('Context: Command dir      = "{}".'.format(self._command_dir))

        self.printer.debug('Context: Repo dir         = "{}".'.format(self._work_repo_dir))
        self.printer.debug('Context: work systems dir = "{}".'.format(self._work_systems_dir))
        self.printer.debug('Context: Custom cleanroom = "{}".'.format(self._sys_cleanroom_dir))
        self.printer.debug('Context: Custom commands  = "{}".'.format(self._sys_commands_dir))

        parser.Parser.find_commands(self)

        self.printer.success('Setting up directories.', verbosity=1)

    def commandsDirectory(self):
        return self._command_dir

    def workDirectory(self):
        return self._directoryCheck(self._work_dir)

    def workRepositoryDirectory(self):
        return self._directoryCheck(self._work_repo_dir)

    def systemsDirectory(self):
        return self._directoryCheck(self._system_dir)

    def systemsCleanRoomDirectory(self):
        return self._directoryCheck(self._sys_cleanroom_dir)

    def systemsCommandsDirectory(self):
        return self._directoryCheck(self._sys_commands_dir)

    def _directoryCheck(self, directory):
        if directory == None:
           raise exceptions.ContextError('Directories not set up yet.')
        return directory

    def priflightCheck(self):
        self.printer.verbose('Running Preflight Checks.')

        binaries = self._preflightBinaries()
        users = self._preflightUsers()

        if not binaries or not users:
            raise exceptions.PreflightError('Preflight Check failed.')

    def _preflightBinaries(self):
        ''' Check executables '''
        passed = True
        for b in self.binaries.items():
            if b[1]:
                self.printer.info('{} found: {}...'.format(b[0], b[1]))
            else:
                self.printer.warn('{} not found.'.format(b[0]))
                passed = False
        return passed

    def _preflightUsers(self):
        ''' Check tha the script is running as root '''
        if os.geteuid() == 0:
            self.printer.verbose('Running as root.')
            return True
        self.printer.warn('Not running as root.')
        return False

