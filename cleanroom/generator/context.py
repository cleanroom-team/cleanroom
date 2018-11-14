# -*- coding: utf-8 -*-
"""The Context the generation will run in.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from ..exceptions import ContextError
from ..printer import debug, h2, info, success, trace

from enum import Enum, auto, unique
import os
import typing


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

    def __init__(self, *,
                 repository: typing.Optional[str]=None,
                 ignore_errors: bool=False,
                 keep_temporary_data: bool=False) -> None:
        """Constructor."""
        self.ignore_errors = ignore_errors
        self.keep_temporary_data = keep_temporary_data
        self._repository = repository

        self._binaries: typing.Dict[Binaries, str] = {}

        self._work_directory: typing.Optional[str] = None
        self._systems_directory: typing.Optional[str] = None
        self._command_directory \
            = os.path.join(os.path.dirname(__file__), 'commands')

    def set_binaries(self, binaries: typing.Dict[Binaries, str]) -> None:
        """Set known binaries."""
        self._binaries = binaries

    def binary(self, selector: Binaries) -> typing.Optional[str]:
        """Get a binary from the context."""
        assert len(self._binaries) > 0

        binary = self._binaries[selector]
        trace('Getting binary for {}: {}.'.format(selector, binary))
        return binary

    def set_directories(self, system_directory: str, work_directory: str) -> None:
        """Set system- and work directory and set them up."""
        h2('Setting up Directories.', verbosity=2)

        if self._systems_directory is not None:
            raise ContextError('Directories were already set up.')

        # main directories:
        self._systems_directory = system_directory
        self._work_directory = work_directory

        info('Context: command directory = "{}".'.format(self._command_directory))
        info('Context: systems directory = "{}".'.format(self._systems_directory))

        debug('Context: work directory    = "{}".'.format(self._work_directory))
        debug('Context: custom commands   = "{}".'.format(self.systems_commands_directory()))
        debug('Context: custom cleanroom  = "{}".'.format(self.systems_cleanroom_directory()))

        success('Setting up directories.', verbosity=3)

    def commands_directory(self) -> typing.Optional[str]:
        """Get the global commands directory."""
        return self._command_directory

    def work_directory(self) -> typing.Optional[str]:
        """Get the top-level work directory."""
        return self._directory_check(self._work_directory)

    @staticmethod
    def current_system_directory_from_work_directory(work_directory: str) -> str:
        """Get the current system directory based on the work_directory."""
        return os.path.join(work_directory, 'current')

    @staticmethod
    def current_directory_from_work_directory(work_directory: str) -> str:
        """Get the current system directory based on the work_directory."""
        return os.path.join(work_directory, 'export')

    def current_system_directory(self) -> typing.Optional[str]:
        """Get the current system directory."""
        return Context.current_system_directory_from_work_directory(
                self._directory_check(self._work_directory))

    @staticmethod
    def storage_directory_from_work_directory(work_directory: str) -> typing.Optional[str]:
        """Get the storage directory based on a work_directory."""
        return os.path.join(work_directory, 'storage')

    def storage_directory(self) -> typing.Optional[str]:
        """Get the top-level storage directory."""
        return Context.storage_directory_from_work_directory(self._directory_check(self._work_directory))

    def systems_directory(self) -> typing.Optional[str]:
        """Get the top-level systems directory."""
        return self._directory_check(self._systems_directory)

    def systems_cleanroom_directory(self) -> typing.Optional[str]:
        """Get the cleanroom configuration directory of a systems directory."""
        return os.path.join(self._directory_check(self._systems_directory), 'cleanroom')

    def systems_commands_directory(self) -> typing.Optional[str]:
        """Get the systems-specific commands directory."""
        return os.path.join(self._directory_check(self.systems_cleanroom_directory()), 'commands')

    def repository(self) -> str:
        """Get the repository to export filesystems into."""
        assert self._repository
        return self._repository

    def _directory_check(self, directory: typing.Optional[str]) -> str:
        """Raise a ContextError if a directory is not yet set up."""
        if directory is None:
            raise ContextError('Directories not set up yet.')
        return directory
