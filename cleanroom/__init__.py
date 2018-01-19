#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from . import parser

from enum import Enum, auto, unique
import os
import os.path
import subprocess


class CleanRoomError(RuntimeError):
    def __init__(self, msg):
        super().__init__(msg)


class PreflightError(CleanRoomError):
    pass


class ContextError(RuntimeError):
    pass


class PrepareError(RuntimeError):
    pass


class GenerateError(RuntimeError):
    pass


def checkForBinary(binary):
    if os.access(binary, os.X_OK):
        return binary
    else:
        return ''


def run(ctx, *args):
    completed_process = subprocess.run(*args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    reportCompletedProcess(ctx.printer.trace, completed_process)
    return completed_process


def reportCompletedProcess(channel, completed_process):
    channel('Arguments  : {}'.format(' '.join(completed_process.args)))
    channel('Return Code: {}'.format(completed_process.returncode))
    channel('StdOut     : {}'.format(completed_process.stdout))
    channel('StdErr     : {}'.format(completed_process.stderr))

@unique
class Binaries(Enum):
    OSTREE = auto()
    ROFILES_FUSE = auto()


@unique
class State(Enum):
    NEW = auto()
    PARSED = auto()
    GENERATING = auto()
    GENERATED = auto()


class Context:
    def __init__(self, printer, force = False, ignore_errors = False):
        self.printer = printer
        self.binaries = {
            Binaries.OSTREE: checkForBinary('/usr/bin/ostree'),
            Binaries.ROFILES_FUSE: checkForBinary('/usr/bin/rofiles-fuse')
        }
        self.generator = Generator(self)

        self.force = force
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
        self.printer.verbose('    Setting up Directories.')

        if self._system_dir != None:
            raise ContextError('Directories were already set up.')

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

        parser.Parser._commands['run'].execute('foo', 'bar', 'baz')

        self.printer.success('Setting up directories.')

    def commandsDirectory(self):
        return self._command_dir

    def workDirectory(self):
        return self._directoryCheck(self._work_dir)

    def workRepositoryDirectory(self):
        return self._directoryCheck(self._work_repo_dir)

    def systemsDirectory(self):
        return self._directoryCheck(self.system_dir)

    def systemsCleanRoomDirectory(self):
        return self._directoryCheck(self._sys_cleanroom_dir)

    def systemsCommandsDirectory(self):
        return self._directoryCheck(self._sys_commands_dir)

    def _directoryCheck(self, directory):
        if directory == None:
           raise ContextError('Directories not set up yet.')
        return directory

    def priflightCheck(self):
        self.printer.verbose('Running Preflight Checks.')

        binaries = self._preflightBinaries()
        users = self._preflightUsers()

        if not binaries or not users:
            raise PreflightError('Preflight Check failed.')

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


class DependencyNode:
    def __init__(self, system, parent, *children):
        self.parent = parent
        self.system = system
        self.state = State.NEW
        self.children = []

    def find(self, system):
        if self.system == system:
            return self

        for cn in children:
            if cn.find(system):
                return cn

        return None


class Generator:
    def __init__(self, ctx):
        self._ctx = ctx
        self.systems = []
        self.dependencies = []
        ctx.generator = self

    def _binary(self, selector):
        return self._ctx.binary(selector)

    def addSystem(self, system):
        node = self._find(system)
        if node:
            return node.parent

        base = parser.Parser(self._ctx, system)

        parentNode = self._find(base)
        node = DependencyNode(system, parentNode)

        if parentNode:
            pass

    def _find(self, system):
        for d in self.dependencies:
            node = d.find(system)
            if node:
                return node

        return None


    def prepare(self):
        repo_dir = self._ctx.workRepositoryDirectory()
        run_result = run(self._ctx,
                         [self._binary(Binaries.OSTREE), 'init', '--repo={}'.format(repo_dir)])
        if run_result.returncode != 0:
            reportCompletedProcess(self._context.print, run_result)
            raise PrepareError('Failed to run ostree init.')

    def generate(self):
        pass


if __name__ == '__main__':
    pass
