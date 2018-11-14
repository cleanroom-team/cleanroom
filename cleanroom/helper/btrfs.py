# -*- coding: utf-8 -*-
"""Helpers for btrfs.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .run import run
from ..printer import trace

import os.path
from subprocess import CompletedProcess
import typing


def run_btrfs(command: typing.Optional[str],
              *args: typing.Any, **kwargs: typing.Any) -> CompletedProcess:
    if command is None:
        command = '/usr/bin/btrfs'
    return run(command, *args, **kwargs)


def create_subvolume(directory: str, *, command: typing.Optional[str]=None):
    """Create a new subvolume."""
    trace('BTRFS: Create subvolume {}.'.format(directory))
    return run_btrfs(command, 'subvolume', 'create', directory,
                     trace_output=trace)


def create_snapshot(source: str, dest: str, *,
                    read_only: bool=False, command: typing.Optional[str]=None) \
        -> CompletedProcess:
    """Create a new snapshot."""
    extra_args: typing.Tuple[str, ...] = ()
    if read_only:
        extra_args = (*extra_args, '-r')

    trace('BTRFS: Create snapshot of {} into {}.'.format(source, dest))
    return run_btrfs(command, 'subvolume', 'snapshot', *extra_args, source, dest,
                     trace_output=trace)


def delete_subvolume(directory: str, *, command: typing.Optional[str]=None) \
        -> CompletedProcess:
    """Delete a subvolume."""
    trace('BTRFS: Delete subvolume {}.'.format(directory))
    result = run_btrfs(command, 'subvolume', 'delete', directory, trace_output=trace)


def delete_subvolume_recursive(directory: str, *, command: typing.Optional[str]=None) \
        -> CompletedProcess:
    """Delete all subvolumes in a subvolume or directory."""
    result = None

    if not directory.endswith('/fs'):
        for f in os.listdir(directory):
            child = os.path.join(directory, f)
            if os.path.isdir(child):
                result = delete_subvolume_recursive(child, command=command)

    if has_subvolume(directory, command=command):
        result = delete_subvolume(directory, command=command)
    return result


def has_subvolume(directory: str, *, command: typing.Optional[str]=None) -> bool:
    """Check whether a subdirectory is a subvolume or snapshot."""
    if not os.path.isdir(directory):
        return False
    result = run(command, 'subvolume', 'show', directory,
                 returncode=None, trace_output=trace)
    return result.returncode == 0
