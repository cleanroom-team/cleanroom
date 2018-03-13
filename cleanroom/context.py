#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The Context the generation will run in.

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
    """Important binaries."""

    OSTREE = auto()
    PACMAN = auto()
    PACMAN_KEY = auto()
    PACSTRAP = auto()
    ROFILES_FUSE = auto()


def _check_for_binary(binary):
    """Check for binaries (with full path!)."""
    return binary if os.access(binary, os.X_OK) else ''


class Context:
    """The context the generation will run in."""

    def Create(verbose=0, ignore_errors=False,
               keep_temporary_data=False):
        """Create a new Context object."""
        prt = printer.Printer(verbose)
        return Context(printer=prt, ignore_errors=ignore_errors,
                       export_repository='/tmp/export_repository',
                       keep_temporary_data=keep_temporary_data)

    def __init__(self, *, printer=None, export_repository=None,
                 ignore_errors=False, keep_temporary_data=False):
        """Constructor."""
        assert(printer)
        assert(export_repository)

        self.printer = printer
        self.binaries = {
            Binaries.OSTREE: _check_for_binary('/usr/bin/ostree'),
            Binaries.PACMAN: _check_for_binary('/usr/bin/pacman'),
            Binaries.PACMAN_KEY: _check_for_binary('/usr/bin/pacman-key'),
            Binaries.PACSTRAP: _check_for_binary('/usr/bin/pacstrap'),
            Binaries.ROFILES_FUSE: _check_for_binary('/usr/bin/rofiles-fuse')
        }
        self.generator = generator.Generator(self)

        self.ignore_errors = ignore_errors
        self.keep_temporary_data = keep_temporary_data

        self._work_directory = None
        self._systems_directory = None
        self._command_directory = None

        self._sys_cleanroom_directory = None
        self._sys_commands_directory = None

        self._export_repository = export_repository

    def binary(self, selector):
        """Get a binary from the context."""
        binary = self.binaries[selector]
        self.printer.trace('Getting binary for {}: {}.'
                           .format(selector, binary))
        return binary

    def set_directories(self, system_directory, work_directory):
        """Set system- and work directory and set them up."""
        self.printer.h2('Setting up Directories.', verbosity=2)

        if self._systems_directory is not None:
            raise exceptions.ContextError('Directories were already set up.')

        # main directories:
        self._systems_directory = system_directory
        self._work_directory = work_directory
        self._command_directory \
            = os.path.join(os.path.dirname(__file__), 'commands')

        self._work_repo_directory = os.path.join(work_directory, 'repo')
        self._work_directory = os.path.join(work_directory, 'systems')

        # setup secondary directories:
        self._sys_cleanroom_directory \
            = os.path.join(self._systems_directory, 'cleanroom')
        self._sys_commands_directory \
            = os.path.join(self._sys_cleanroom_directory, 'commands')

        self.printer.info('Context: Systems directory = "{}".'
                          .format(self._systems_directory))
        self.printer.info('Context: Work directory    = "{}".'
                          .format(self._work_directory))
        self.printer.info('Context: Command directory = "{}".'
                          .format(self._command_directory))

        self.printer.debug('Context: Repo directory   = "{}".'
                           .format(self._work_repo_directory))
        self.printer.debug('Context: work directory   = "{}".'
                           .format(self._work_directory))
        self.printer.debug('Context: Custom cleanroom = "{}".'
                           .format(self._sys_cleanroom_directory))
        self.printer.debug('Context: Custom commands  = "{}".'
                           .format(self._sys_commands_directory))

        parser.Parser.find_commands(self)

        self.printer.success('Setting up directories.', verbosity=3)

    def commands_directory(self):
        """Get the global commands directory."""
        return self._command_directory

    def work_directory(self):
        """Get the top-level work directory."""
        return self._directory_check(self._work_directory)

    def work_repository_directory(self):
        """Get the ostree repository directory."""
        return self._directory_check(self._work_repo_directory)

    def systems_directory(self):
        """Get the top-level systems directory."""
        return self._directory_check(self._systems_directory)

    def system_definition_directory(self, system):
        """Get the top-level directory of the given system."""
        return os.path.join(self.systems_directory(), system)

    def systems_cleanroom_directory(self):
        """Get the cleanroom configuration directory of a systems directory."""
        return self._directory_check(self._sys_cleanroom_directory)

    def systems_commands_directory(self):
        """Get the systems-specific commands directory."""
        return self._directory_check(self._sys_commands_directory)

    def export_repository(self):
        """Get the repository to export filesystems into."""
        return self._export_repository

    def _directory_check(self, directory):
        """Raise a ContextError if a directory is not yet set up."""
        if directory is None:
            raise exceptions.ContextError('Directories not set up yet.')
        return directory

    def preflight_check(self):
        """Run a fast pre-flight check on the context."""
        self.printer.h2('Running Preflight Checks.', verbosity=2)

        binaries = self._preflight_binaries_check()
        users = self._preflight_users_check()

        if not binaries or not users:
            raise exceptions.PreflightError('Preflight Check failed.')

    def _preflight_binaries_check(self):
        """Check executables."""
        passed = True
        for b in self.binaries.items():
            if b[1]:
                self.printer.info('{} found: {}...'.format(b[0], b[1]))
            else:
                self.printer.warn('{} not found.'.format(b[0]))
                passed = False
        return passed

    def _preflight_users_check(self):
        """Check tha the script is running as root."""
        if os.geteuid() == 0:
            self.printer.debug('Running as root.')
            return True
        self.printer.warn('Not running as root.')
        return False
