# -*- coding: utf-8 -*-
"""Handle mounts.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from ..printer import trace, none
from .run import run

import re
import os
import stat
import typing


def _map_into_chroot(directory: str, chroot: typing.Optional[str] = None):
    assert os.path.isabs(directory)
    directory = os.path.normpath(directory)

    if chroot:
        chroot = os.path.normpath(chroot)
        while chroot.endswith("/") and chroot != "/":
            chroot = chroot[:-1]
        full_path = os.path.normpath(chroot + "/" + directory)
        assert full_path.startswith(chroot + "/")
        return full_path

    return directory


def mount_points(
    directory: str, chroot: typing.Optional[str] = None
) -> typing.List[str]:
    """Return a list of mount points at or below the given directory."""
    assert not directory.endswith("/")
    directory = _map_into_chroot(directory, chroot)

    pattern = re.compile("^(.*) on (.*) type (.*)$")
    result = run("/usr/bin/mount", trace_output=none)
    sub_mounts: typing.List[str] = []
    for line in result.stdout.split("\n"):
        if not line:
            continue
        match = re.match(pattern, line)
        assert match
        mount_point = match.group(2)

        if mount_point == directory or mount_point.startswith(directory + "/"):
            trace("Mount point: {}.".format(mount_point))
            sub_mounts.append(mount_point)

    return sorted(sub_mounts, key=len, reverse=True)


def umount(directory: str, chroot: typing.Optional[str] = None) -> None:
    """Umount a directory."""
    assert len(mount_points(directory)) == 1

    run("/usr/bin/umount", _map_into_chroot(directory, chroot))

    assert len(mount_points(directory)) == 0


def umount_all(directory: str, chroot: typing.Optional[str] = None) -> bool:
    """Umount all mount points below a directory."""
    sub_mounts = mount_points(directory, chroot=chroot)

    if sub_mounts:
        for mp in sub_mounts:
            umount(mp)

        sub_mounts = mount_points(directory, chroot=chroot)

    return len(sub_mounts) == 0


def mount(
    volume: str,
    directory: str,
    *,
    options: str = "",
    fs_type: str = "",
    chroot: str = ""
) -> None:
    assert len(mount_points(directory)) == 0

    args: typing.List[str] = ["-t", fs_type] if fs_type else []
    args += ["-o", options] if options else []

    is_pseudo = (
        volume == "proc"
        or volume == "sys"
        or volume == "udev"
        or volume == "devpts"
        or volume == "shm"
        or volume == "tmp"
    )

    if (
        chroot
        and not is_pseudo
        and not volume.startswith("/dev/")
        and not volume.startswith("/sys/")
    ):
        volume = _map_into_chroot(volume, chroot)

    target = _map_into_chroot(directory, chroot)

    is_loop = "loop" in options.split(",")
    is_bind = "bind" in options.split(",")
    if is_pseudo:
        is_block = False
    else:
        is_block = stat.S_ISBLK(os.stat(volume).st_mode)
    assert (not is_loop and (is_block or is_pseudo or is_bind)) or (
        is_loop and os.path.isfile(volume)
    )
    assert os.path.isdir(target)

    args += [volume, target]

    run("/usr/bin/mount", *args)

    assert len(mount_points(directory)) == 1


class Mount:
    def __init__(
        self,
        volume: str,
        directory: str,
        *,
        options: str = "",
        fs_type: str = "",
        chroot: str = "",
        must_exist: bool = False,
        fallback_cwd: str = ""
    ) -> None:
        self._volume = volume
        self._fallback_cwd = fallback_cwd
        self._must_remove_mount_point = False
        if chroot and not volume.startswith("/dev/") and not volume.startswith("/sys/"):
            self._volume = _map_into_chroot(volume, chroot)

        self._directory = _map_into_chroot(directory, chroot)

        if os.path.exists(self._directory):
            if not os.path.isdir(self._directory):
                raise OSError(
                    'Mount point "{}" is not a directory.'.format(self._directory)
                )
        else:
            if must_exist:
                raise OSError(
                    'Mount point "{}" does not exist.'.format(self._directory)
                )
            else:
                self._must_remove_mount_point = True
                os.makedirs(self._directory)

        self._options = options
        self._fs_type = fs_type

    def __enter__(self) -> typing.Any:
        mount(
            self._volume, self._directory, options=self._options, fs_type=self._fs_type
        )
        return self._directory

    def __exit__(
        self, exc_type: typing.Any, exc_val: typing.Any, exc_tb: typing.Any
    ) -> None:
        if self._fallback_cwd:
            os.chdir(self._fallback_cwd)
        umount(self._directory)
        if self._must_remove_mount_point:
            os.rmdir(self._directory)
