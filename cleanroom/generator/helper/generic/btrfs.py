# -*- coding: utf-8 -*-
"""Helpers for btrfs.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.context import Binaries
from cleanroom.generator.systemcontext import SystemContext

import cleanroom.helper.btrfs as btrfs


def _binary(ctx):
    if isinstance(ctx, SystemContext):
        return ctx.ctx.binary(Binaries.BTRFS)
    return ctx.binary(Binaries.BTRFS)


def create_subvolume(ctx, name):
    """Create a new subvolume."""
    return btrfs.create_subvolume(name, command=_binary(ctx))


def create_snapshot(ctx, source, dest, *, read_only=False):
    """Create a new snapshot."""
    return btrfs.create_snapshot(source, dest, read_only=False, command=_binary(ctx))


def delete_subvolume(ctx, name):
    """Delete a subvolume."""
    return btrfs.delete_subvolume(name, command=_binary(ctx))


def has_subvolume(ctx, name):
    """Check whether a subdirectory is a subvolume or snapshot."""
    return btrfs.has_subvolume(name, command=_binary(ctx))
