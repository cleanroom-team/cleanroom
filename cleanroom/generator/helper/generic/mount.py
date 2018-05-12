# -*- coding: utf-8 -*-
"""Handle mounts.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.helper.run import run

import re


def _mount_points(directory):
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


def mount_points(system_context, directory):
    """Return a list of mount points at or below a directory of the system."""
    return map(lambda d: d[len(directory) + 1:],
               _mount_points(system_context.file_name(directory)))


def _umount(directory):
    """Unmount a directory."""
    run('/usr/bin/umount', directory)


def umount(system_context, directory):
    """Unmount a directory of the system."""
    return _umount(system_context.file_name(directory))


def _umount_all(directory):
    """Unmount all mount points below a directory."""
    mount_points = _mount_points(directory)

    if mount_points:
        for mp in mount_points:
            _umount(mp)

        mount_points = _mount_points(directory)

    return len(mount_points) == 0


def umount_all(system_context, directory):
    """Unmount all mount points below a directory of a system."""
    return _umount_all(system_context.file_name(directory))
