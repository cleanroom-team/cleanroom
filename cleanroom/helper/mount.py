# -*- coding: utf-8 -*-
"""Handle mounts.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from .run import run

import re
import os.path
import typing


def _map_into_chroot(directory: str, chroot: typing.Optional[str]):
    assert os.path.isabs(directory)
    directory = os.path.normpath(directory)

    if chroot is not None:
        chroot = os.path.normpath(chroot)
        while chroot.endswith('/') and chroot != '/':
            chroot = chroot[:-1]
        full_path = os.path.normpath(chroot + '/' + directory)
        assert full_path.startswith(chroot + '/')
        return full_path

    return directory


def mount_points(directory: str, chroot: typing.Optional[str] = None) \
        -> typing.List[str]:
    """Return a list of mount points at or below the given directory."""
    assert (not directory.endswith('/'))
    directory = _map_into_chroot(directory, chroot)

    pattern = re.compile('^(.*) on (.*) type (.*)$')
    result = run('/usr/bin/mount')
    sub_mounts: typing.List[str] = []
    for line in result.stdout.split('\n'):
        if not line:
            continue
        match = re.match(pattern, line)
        assert match
        mount_point = match.group(2)

        if mount_point == directory or \
                mount_point.startswith(directory + '/'):
            sub_mounts.append(mount_point)

    return sorted(sub_mounts, key=len, reverse=True)


def umount(directory: str, chroot: typing.Optional[str] = None) -> None:
    """Unmount a directory."""
    run('/usr/bin/umount', _map_into_chroot(directory, chroot))


def umount_all(directory: str, chroot: typing.Optional[str] = None) -> bool:
    """Unmount all mount points below a directory."""
    sub_mounts = mount_points(directory, chroot=chroot)

    if sub_mounts:
        for mp in sub_mounts:
            umount(mp)

        sub_mounts = mount_points(directory, chroot=chroot)

    return len(sub_mounts) == 0


def mount(volume: str, directory: str, *,
          options: typing.Optional[str] = None,
          fs_type: typing.Optional[str] = None,
          chroot: typing.Optional[str] = None) -> None:
    args: typing.List[str] = []
    if fs_type is not None:
        args += ['-t', fs_type]
    if options is not None:
        args += ['-o', options]

    if chroot is not None \
            and not volume.startswith('/dev/') \
            and not volume.startswith('/sys/'):
        volume = _map_into_chroot(volume, chroot)

    args += [volume, _map_into_chroot(directory, chroot)]

    run('/usr/bin/mount', *args)
