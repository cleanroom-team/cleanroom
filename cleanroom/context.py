# -*- coding: utf-8 -*-
"""The Context the generation will run in.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.exceptions as ex
import cleanroom.printer as printer

from enum import Enum, auto, unique
import os


@unique
class Binaries(Enum):
    """Important binaries."""

    BORG = auto()
    BTRFS = auto()
    PACMAN = auto()
    PACMAN_KEY = auto()
    PACSTRAP = auto()
    SBSIGN = auto()
    OBJCOPY = auto()
    MKSQUASHFS = auto()
    VERITYSETUP = auto()


class Context:
    """The context the generation will run in."""

    def __init__(self, *, export_repository=None,
                 ignore_errors=False, keep_temporary_data=False):
        """Constructor."""
        self.ignore_errors = ignore_errors
        self.keep_temporary_data = keep_temporary_data
        self._export_repository = export_repository

        self._binaries = {}

        self._work_directory = None
        self._systems_directory = None
        self._command_directory \
            = os.path.join(os.path.dirname(__file__), 'commands')

    def set_binaries(self, binaries):
        """Set known binaries."""
        self._binaries = binaries

    def binary(self, selector):
        """Get a binary from the context."""
        assert(len(self._binaries) > 0)

        binary = self._binaries[selector]
        printer.trace('Getting binary for {}: {}.'.format(selector, binary))
        return binary

    def set_directories(self, system_directory, work_directory):
        """Set system- and work directory and set them up."""
        printer.h2('Setting up Directories.', verbosity=2)

        if self._systems_directory is not None:
            raise ex.ContextError('Directories were already set up.')

        # main directories:
        self._systems_directory = system_directory
        self._work_directory = work_directory

        printer.verbose('Context: command directory = "{}".'
                        .format(self._command_directory))
        printer.verbose('Context: systems directory = "{}".'
                        .format(self._systems_directory))

        printer.info('Context: work directory    = "{}".'
                     .format(self._work_directory))
        printer.info('Context: custom cleanroom  = "{}".'
                     .format(self.systems_cleanroom_directory()))
        printer.info('Context: custom commands   = "{}".'
                     .format(self.systems_commands_directory()))

        printer.success('Setting up directories.', verbosity=3)

    def commands_directory(self):
        """Get the global commands directory."""
        return self._command_directory

    def work_directory(self):
        """Get the top-level work directory."""
        return self._directory_check(self._work_directory)

    @staticmethod
    def current_system_directory_from_work_directory(work_directory):
        """Get the current system directory based on the work_directory."""
        return os.path.join(work_directory, 'current')

    @staticmethod
    def current_export_directory_from_work_directory(work_directory):
        """Get the current system directory based on the work_directory."""
        return os.path.join(work_directory, 'export')

    def current_system_directory(self):
        """Get the current system directory."""
        return self._directory_check(
            Context.current_system_directory_from_work_directory(
                self._work_directory))

    @staticmethod
    def storage_directory_from_work_directory(work_directory):
        """Get the storage directory based on a work_directory."""
        return os.path.join(work_directory, 'storage')

    def storage_directory(self):
        """Get the top-level storage directory."""
        return self._directory_check(
            os.path.join(Context.storage_directory_from_work_directory(
                self._work_directory)))

    def systems_directory(self):
        """Get the top-level systems directory."""
        return self._directory_check(self._systems_directory)

    def systems_cleanroom_directory(self):
        """Get the cleanroom configuration directory of a systems directory."""
        return self._directory_check(os.path.join(self._systems_directory,
                                                  'cleanroom'))

    def systems_commands_directory(self):
        """Get the systems-specific commands directory."""
        return self._directory_check(
            os.path.join(self.systems_cleanroom_directory(), 'commands'))

    def export_repository(self):
        """Get the repository to export filesystems into."""
        assert(self._export_repository)
        return self._export_repository

    def _directory_check(self, directory):
        """Raise a ContextError if a directory is not yet set up."""
        if self._work_directory is None:
            raise ex.ContextError('Directories not set up yet.')
        return directory
