# -*- coding: utf-8 -*-
"""Helpers for btrfs.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .run import run
from ..printer import trace

from subprocess import CompletedProcess
import typing


def run_btrfs(command: typing.Optional[str],
              *args: typing.Any, **kwargs: typing.Any) -> CompletedProcess:
    if command is None:
        command = '/usr/bin/btrfs'
    return run(command, *args, **kwargs)


def create_subvolume(name: str, *, command: typing.Optional[str]=None):
    """Create a new subvolume."""
    return run_btrfs(command, 'subvolume', 'create', name,
                     trace_output=trace)


def create_snapshot(source: str, dest: str, *,
                    read_only: bool=False, command: typing.Optional[str]=None) \
        -> CompletedProcess:
    """Create a new snapshot."""
    extra_args: typing.Tuple[str, ...] = ()
    if read_only:
        extra_args = (*extra_args, '-r')

    return run_btrfs(command, 'subvolume', 'snapshot', *extra_args, source, dest,
                     trace_output=trace)


def delete_subvolume(name: str, *, command: typing.Optional[str]=None) \
        -> CompletedProcess:
    """Delete a subvolume."""
    return run_btrfs(command, 'subvolume', 'delete', name, trace_output=trace)


def has_subvolume(name: str, *, command: typing.Optional[str]=None) -> bool:
    """Check whether a subdirectory is a subvolume or snapshot."""
    result = run(command, 'subvolume', 'show', name,
                 returncode=None, trace_output=trace)
    return result.returncode == 0
