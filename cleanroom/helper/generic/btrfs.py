# -*- coding: utf-8 -*-
"""Helpers for btrfs.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.context as context
import cleanroom.helper.generic.run as run
import cleanroom.printer as printer
import cleanroom.systemcontext as systemcontext


def _find_ctx(ctx):
    if isinstance(ctx, systemcontext.SystemContext):
        return ctx.ctx
    return ctx


def create_subvolume(ctx, name):
    """Create a new subvolume."""
    ctx = _find_ctx(ctx)

    run.run(ctx.binary(context.Binaries.BTRFS),
            'subvolume', 'create', name, trace_output=printer.trace)


def create_snapshot(ctx, source, dest, *, read_only=False):
    """Create a new snapshot."""
    ctx = _find_ctx(ctx)

    extra_args = ()
    if read_only:
        extra_args = (*extra_args, '-r')

    run.run(ctx.binary(context.Binaries.BTRFS),
            'subvolume', 'snapshot', *extra_args, source, dest,
            trace_output=printer.trace)


def delete_subvolume(ctx, name):
    """Delete a subvolume."""
    ctx = _find_ctx(ctx)

    run.run(ctx.binary(context.Binaries.BTRFS),
            'subvolume', 'delete', name, trace_output=printer.trace)


def has_subvolume(ctx, name):
    """Check whether a subdirectory is a subvolume or snapshot."""
    ctx = _find_ctx(ctx)

    result = run.run(ctx.binary(context.Binaries.BTRFS),
                     'subvolume', 'show', name,
                     exit_code=None, trace_output=printer.trace)
    return result.returncode == 0
