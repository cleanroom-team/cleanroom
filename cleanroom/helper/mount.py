# -*- coding: utf-8 -*-
"""Handle mounts.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .run import run

import re


def mount_points(directory):
    """Return a list of mount points at or below the given directory."""
    assert(not directory.endswith('/'))

    pattern = re.compile('^(.*) on (.*) type (.*)$')
    result = run('/usr/bin/mount')
    mount_points = []
    for line in result.stdout.split('\n'):
        if not line:
            continue
        match = re.match(pattern, line)
        assert(match)
        mount_point = match.group(2)

        if mount_point == directory or \
           mount_point.startswith(directory + '/'):
            mount_points.append(mount_point)

    return sorted(mount_points, key=len, reverse=True)


def umount(directory):
    """Unmount a directory."""
    run('/usr/bin/umount', directory)


def umount_all(directory):
    """Unmount all mount points below a directory."""
    mount_points = _mount_points(directory)

    if mount_points:
        for mp in mount_points:
            _umount(mp)

        mount_points = _mount_points(directory)

    return len(mount_points) == 0


def mount(volume, directory, *, options=None, type=None):
    args = []
    if type is not None:
        args += ['-t', type]
    if options is not None:
        args += ['-o', options]

    args += [volume, directory]
    run('/usr/bin/mount', args)
