# -*- coding: utf-8 -*-
"""Handle mounts.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from .run import run

import re
import os.path


def _map_into_chroot(directory, chroot):
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


def mount_points(directory, chroot=None):
    """Return a list of mount points at or below the given directory."""
    assert (not directory.endswith('/'))
    directory = _map_into_chroot(directory, chroot)

    pattern = re.compile('^(.*) on (.*) type (.*)$')
    result = run('/usr/bin/mount')
    mount_points = []
    for line in result.stdout.split('\n'):
        if not line:
            continue
        match = re.match(pattern, line)
        assert (match)
        mount_point = match.group(2)

        if mount_point == directory or \
                mount_point.startswith(directory + '/'):
            mount_points.append(mount_point)

    return sorted(mount_points, key=len, reverse=True)


def umount(directory, chroot=None):
    """Unmount a directory."""
    run('/usr/bin/umount', _map_into_chroot(directory, chroot))


def umount_all(directory, chroot=None):
    """Unmount all mount points below a directory."""
    mount_points = mount_points(directory, chroot=chroot)

    if mount_points:
        for mp in mount_points:
            umount(mp)

        mount_points = mount_points(directory, chroot=chroot)

    return len(mount_points) == 0


def mount(volume, directory, *, options=None, type=None, chroot=None):
    args = []
    if type is not None:
        args += ['-t', type]
    if options is not None:
        args += ['-o', options]

    if chroot is not None \
            and not volume.startswith('/dev/') \
            and not volume.startswith('/sys/'):
        volume = _map_into_chroot(volume, chroot)

    args += [volume, _map_into_chroot(directory, chroot)]
    run('/usr/bin/mount', args)
