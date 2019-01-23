# -*- coding: utf-8 -*-
"""Helpers for btrfs.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from ..printer import trace
from .run import run

import os.path
import typing


class BtrfsHelper:
    def __init__(self, btrfs_command):
        assert btrfs_command
        self._command = btrfs_command

    def create_subvolume(self, directory: str) -> None:
        """Create a new subvolume."""
        trace('BTRFS: Create subvolume {}.'.format(directory))
        run(self._command, 'subvolume', 'create', directory, trace_output=trace)

    def create_snapshot(self, source: str, destination: str, *,
                        read_only: bool = False) -> None:
        """Create a new snapshot."""
        extra_args: typing.Tuple[str, ...] = ()
        if read_only:
            extra_args = (*extra_args, '-r')

        trace('BTRFS: Create snapshot of {} into {} ({}).'
              .format(source, destination, 'ro' if read_only else 'rw'))
        run(self._command, 'subvolume', 'snapshot', *extra_args, source, destination,
            trace_output=trace)

    def delete_subvolume(self, directory: str) -> None:
        """Delete a subvolume."""
        trace('BTRFS: Delete subvolume {}.'.format(directory))
        run(self._command, 'subvolume', 'delete', directory, trace_output=trace)

    def delete_subvolume_recursive(self, directory: str) -> None:
        """Delete all subvolumes in a subvolume or directory."""
        for f in os.listdir(directory):
            child = os.path.join(directory, f)
            if os.path.isdir(child):
                self.delete_subvolume_recursive(child)

        if self.has_subvolume(directory):
            self.delete_subvolume(directory)

    def has_subvolume(self, directory: str) -> bool:
        """Check whether a subdirectory is a subvolume or snapshot."""
        if not os.path.isdir(directory):
            return False
        return run(self._command, 'subvolume', 'show', directory,
                   return_code=None, trace_output=trace).returncode == 0

    def is_btrfs_filesystem(self, directory: str) -> bool:
        if not os.path.isdir(directory):
            return False
        return run(self._command, 'subvolume', 'list', directory,
                   return_code=None, trace_output=trace).returncode == 0
