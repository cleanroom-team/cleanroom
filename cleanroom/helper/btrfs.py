# -*- coding: utf-8 -*-
"""Helpers for btrfs.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .run import run
from ..printer import trace


def run_btrfs(command, *args, **kwargs):
    if command is None:
        command = '/usr/bin/btrfs'
    return run(command, *args, **kwargs)


def create_subvolume(name, command=None):
    """Create a new subvolume."""
    run_btrfs(command, 'subvolume', 'create', name,
              trace_output=trace)


def create_snapshot(source, dest, *, read_only=False, command=None):
    """Create a new snapshot."""
    extra_args = ()
    if read_only:
        extra_args = (*extra_args, '-r')

    run_btrfs(command, 'subvolume', 'snapshot', *extra_args, source, dest,
              trace_output=trace)


def delete_subvolume(name, command=None):
    """Delete a subvolume."""
    run_btrfs(command, 'subvolume', 'delete', name, trace_output=trace)


def has_subvolume(name, command=None):
    """Check whether a subdirectory is a subvolume or snapshot."""
    result = run(command, 'subvolume', 'show', name,
                 exit_code=None, trace_output=trace)
    return result.returncode == 0
