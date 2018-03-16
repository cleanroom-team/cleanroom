#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helpers for btrfs.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.context as context
import cleanroom.runcontext as runcontext
import cleanroom.helper.generic.run as run


def create_subvolume(ctx, name):
    """Create a new subvolume."""
    if isinstance(ctx, runcontext.RunContext):
        ctx = ctx.ctx

    run.run(ctx.binary(context.Binaries.BTRFS),
            'subvolume', 'create', name, trace_output=ctx.printer.trace)


def create_snapshot(ctx, source, dest, *, read_only=False):
    """Create a new snapshot."""
    if isinstance(ctx, runcontext.RunContext):
        ctx = ctx.ctx

    extra_args = ()
    if read_only:
        extra_args = (*extra_args, '-r')

    run.run(ctx.binary(context.Binaries.BTRFS),
            'subvolume', 'snapshot', *extra_args, source, dest,
            trace_output=ctx.printer.trace)


def delete_subvolume(ctx, name):
    """Delete a subvolume."""
    if isinstance(ctx, runcontext.RunContext):
        ctx = ctx.ctx

    run.run(ctx.binary(context.Binaries.BTRFS),
            'subvolume', 'delete', name, trace_output=ctx.printer.trace)


def has_subvolume(ctx, name):
    """Check whether a subdirectory is a subvolume or snapshot."""
    if isinstance(ctx, runcontext.RunContext):
        ctx = ctx.ctx

    result = run.run(ctx.binary(context.Binaries.BTRFS),
                     'subvolume', 'show', name,
                     exit_code=None, trace_output=ctx.printer.trace)
    return result.returncode == 0


if __name__ == '__main__':
    pass
