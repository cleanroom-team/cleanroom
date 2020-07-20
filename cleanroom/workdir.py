# -*- coding: utf-8 -*-
"""Create and manage the work directory.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .exceptions import PreflightError
from .helper.btrfs import BtrfsHelper
from .helper.mount import umount_all
from .printer import debug, info, trace

import os
import os.path
import tempfile
import typing


def _ensure_directory(directory: str, btrfs_helper: BtrfsHelper) -> None:
    if not os.path.isdir(directory):
        btrfs_helper.create_subvolume(directory)
        btrfs_helper.set_property(directory, name="compression", value="none")
        if not os.path.isdir(directory):
            raise PreflightError(
                "Failed to set up work directory: " "{} not created.".format(directory)
            )


def _clear_directory(directory: str, btrfs_helper: BtrfsHelper) -> None:
    trace("Cleaning directory: {}.".format(directory))
    umount_all(directory)

    if os.path.isdir(directory):
        # Fast path:-)
        btrfs_helper.delete_subvolume(os.path.join(directory, "fs"))
        btrfs_helper.delete_subvolume(os.path.join(directory, "meta"))
        btrfs_helper.delete_subvolume(os.path.join(directory, "cache"))
        btrfs_helper.delete_subvolume(directory)

        # Slow fallback path:
        if not os.path.isdir(directory):
            return
        btrfs_helper.delete_subvolume_recursive(directory)
        if os.path.isdir(directory):
            os.rmdir(directory)


class WorkDir:
    """Parse a container.conf file."""

    def __init__(
        self,
        btrfs_helper: BtrfsHelper,
        *,
        work_directory: str,
        clear_scratch_directory: bool = False,
        clear_storage: bool = False
    ) -> None:
        """Constructor."""
        self._btrfs_helper = btrfs_helper
        self._work_directory = work_directory
        self._temp_directory: typing.Optional[tempfile.TemporaryDirectory[str]] = None

        if work_directory:
            if not os.path.exists(work_directory):
                trace(
                    'Creating permanent work directory in "{}".'.format(work_directory)
                )
                os.makedirs(work_directory, 0o700)
            else:
                if not btrfs_helper.is_btrfs_filesystem(work_directory):
                    raise PreflightError(
                        '"{}" is not on a btrfs filesystem.'.format(self.work_directory)
                    )

                trace('Using existing work directory in "{}".'.format(work_directory))
                if not umount_all(work_directory):
                    raise PreflightError(
                        "Failed to umount all in work "
                        'directory "{}".'.format(work_directory)
                    )
                if clear_scratch_directory:
                    self.clear_scratch_directory()
                if clear_storage:
                    self.clear_storage_directory()
        else:
            trace("Creating temporary work directory.")
            self._temp_directory = tempfile.TemporaryDirectory(
                prefix="clrm-", dir="/var/tmp"
            )
            self._work_directory = self._temp_directory.name

        self._setup_work_directory()

    def __del__(self) -> None:
        """Destructor."""
        self.cleanup()

    def __enter__(self) -> typing.Any:
        """Enter a Context."""
        if self._temp_directory:
            self._temp_directory.__enter__()
        return self

    def __exit__(self, exc_type: typing.Any, exc_val: typing.Any, exc_tb: typing.Any):
        """Exit a context."""
        if self._temp_directory:
            tmp_directory = self._temp_directory
            self._temp_directory = None
            tmp_directory.__exit__(exc_type, exc_val, exc_tb)

        return False

    def cleanup(self) -> None:
        """Clean up the work directory (if necessary)."""
        if self._temp_directory:
            self._temp_directory.cleanup()
            self._temp_directory = None

    @property
    def scratch_directory(self) -> str:
        """Get the system directory."""
        return os.path.join(self._work_directory, "scratch")

    def clear_scratch_directory(self) -> None:
        _clear_directory(self.scratch_directory, self._btrfs_helper)
        _ensure_directory(self.scratch_directory, self._btrfs_helper)

    @property
    def storage_directory(self) -> str:
        """Get the storage directory."""
        return os.path.join(self._work_directory, "storage")

    def clear_storage_directory(self) -> None:
        # Trigger fast-path on storage directories:
        if not os.path.isdir(self.storage_directory):
            return  # no storage directory, nothing to do:-)
        with os.scandir(self.storage_directory) as it:
            for entry in it:
                if entry.is_dir():
                    _clear_directory(entry.path, self._btrfs_helper)

        # slow path:
        _clear_directory(self.storage_directory, self._btrfs_helper)

    @property
    def work_directory(self) -> str:
        """Get the work directory based."""
        return self._work_directory

    def _setup_work_directory(self) -> None:
        _ensure_directory(self.storage_directory, self._btrfs_helper)
        _ensure_directory(self.scratch_directory, self._btrfs_helper)

        info('WorkDir: work directory     = "{}".'.format(self.work_directory))
        debug('WorkDir: scratch directory  = "{}".'.format(self.scratch_directory))
        debug('WorkDir: storage directory  = "{}".'.format(self.storage_directory))
