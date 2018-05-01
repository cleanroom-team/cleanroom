# -*- coding: utf-8 -*-
"""Create and manage the work directory.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.context as context
import cleanroom.exceptions as ex
import cleanroom.helper.generic.btrfs as btrfs
import cleanroom.helper.generic.mount as mount
import cleanroom.printer as printer

import os
import os.path
import tempfile


class WorkDir:
    """Parse a container.conf file."""

    def __init__(self, ctx, *, work_directory=None,
                 clear_work_directory=False,
                 clear_storage=False):
        """Constructor."""
        self._path = work_directory
        self._temp_directory = None

        if work_directory:
            if not os.path.exists(work_directory):
                printer.trace('Creating permanent work directory in "{}".'
                              .format(work_directory))
                os.makedirs(work_directory, 0o700)
            else:
                printer.trace('Using existing work directory in "{}".'
                              .format(work_directory))
                if not mount._umount_all(work_directory):
                    raise ex.PrepareError('Failed to unmount mount in '
                                          'work directory "{}".'
                                          .format(work_directory))
                if clear_work_directory:
                    _clear_work_directory(ctx, work_directory)
                if clear_storage:
                    _clear_storage(ctx, work_directory)
        else:
            printer.trace('Creating temporary work directory.')
            self._temp_directory = tempfile.TemporaryDirectory(prefix='clrm-',
                                                               dir='/var/tmp')
            self._path = self._temp_directory.name

    def __del__(self):
        """Destructor."""
        self.cleanup()

    def __enter__(self):
        """Enter a Context."""
        if self._temp_directory:
            return self._temp_directory.__enter__()
        else:
            return self._path

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit a context."""
        if (self._temp_directory):
            tmpDir = self._temp_directory
            self._temp_directory = None
            return tmpDir.__exit__(exc_type, exc_val, exc_tb)
        return False

    def path(self):
        """Name of the work directory."""
        return self._path

    def cleanup(self):
        """Clean up the work directory (if necessary)."""
        if not self._temp_directory:
            return

        self._temp_directory.cleanup()
        self._temp_directory = None


def _subdirectories(dir):
    return [os.path.join(dir, name) for name in os.listdir(dir)
            if os.path.isdir(os.path.join(dir, name))]


def _delete_subvolume(ctx, dir):
    if btrfs.has_subvolume(ctx, dir):
        btrfs.delete_subvolume(ctx, dir)


def _clear_work_directory(ctx, work_directory):
    _delete_subvolume(ctx, context.Context
                      .current_export_directory_from_work_directory(
                          work_directory))
    _delete_subvolume(ctx, context.Context
                      .current_system_directory_from_work_directory(
                          work_directory))


def _clear_storage(ctx, work_directory):
    storage_directory \
        = context.Context.storage_directory_from_work_directory(
            work_directory)
    if os.path.isdir(storage_directory):
        for path in _subdirectories(storage_directory):
            _delete_subvolume(ctx, path)
        os.rmdir(storage_directory)
