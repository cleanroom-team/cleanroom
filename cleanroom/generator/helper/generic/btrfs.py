# -*- coding: utf-8 -*-
"""Helpers for btrfs.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.context import Binaries
from cleanroom.generator.helper.generic.run import run
from cleanroom.generator.systemcontext import SystemContext

from cleanroom.printer import trace


def _find_ctx(ctx):
    if isinstance(ctx, SystemContext):
        return ctx.ctx
    return ctx


def create_subvolume(ctx, name):
    """Create a new subvolume."""
    ctx = _find_ctx(ctx)

    run(ctx.binary(Binaries.BTRFS), 'subvolume', 'create',
        name, trace_output=trace)


def create_snapshot(ctx, source, dest, *, read_only=False):
    """Create a new snapshot."""
    ctx = _find_ctx(ctx)

    extra_args = ()
    if read_only:
        extra_args = (*extra_args, '-r')

    run(ctx.binary(Binaries.BTRFS), 'subvolume', 'snapshot',
        *extra_args, source, dest, trace_output=trace)


def delete_subvolume(ctx, name):
    """Delete a subvolume."""
    ctx = _find_ctx(ctx)

    run(ctx.binary(Binaries.BTRFS), 'subvolume', 'delete',
        name, trace_output=trace)


def has_subvolume(ctx, name):
    """Check whether a subdirectory is a subvolume or snapshot."""
    ctx = _find_ctx(ctx)

    result = run(ctx.binary(Binaries.BTRFS),
                 'subvolume', 'show', name,
                 exit_code=None, trace_output=trace)
    return result.returncode == 0
