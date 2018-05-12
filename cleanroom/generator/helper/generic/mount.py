# -*- coding: utf-8 -*-
"""Handle mounts.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.helper.mount as mount


def mount_points(system_context, directory):
    """Return a list of mount points at or below a directory of the system."""
    return map(lambda d: d[len(directory) + 1:],
               mount.mount_points(system_context.file_name(directory)))


def umount(system_context, directory):
    """Unmount a directory of the system."""
    return mount.umount(system_context.file_name(directory))


def umount_all(system_context, directory):
    """Unmount all mount points below a directory of a system."""
    return mount.umount_all(system_context.file_name(directory))
