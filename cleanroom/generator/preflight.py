# -*- coding: utf-8 -*-
"""The Context the generation will run in.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .context import Binaries, Context
from ..exceptions import PreflightError
from ..printer import (debug, info, h2, warn,)

import os


def _check_for_binary(binary: str) -> str:
    """Check for binaries (with full path!)."""
    return binary if os.access(binary, os.X_OK) else ''


def _find_binaries(ctx: Context) -> None:
    ctx.set_binaries({
        Binaries.BORG: _check_for_binary('/usr/bin/borg'),
        Binaries.BTRFS: _check_for_binary('/usr/bin/btrfs'),
        Binaries.PACMAN: _check_for_binary('/usr/bin/pacman'),
        Binaries.PACMAN_KEY: _check_for_binary('/usr/bin/pacman-key'),
        Binaries.PACSTRAP: _check_for_binary('/usr/bin/pacstrap'),
        Binaries.SBSIGN: _check_for_binary('/usr/bin/sbsign'),
        Binaries.OBJCOPY: _check_for_binary('/usr/bin/objcopy'),
        Binaries.MKSQUASHFS: _check_for_binary('/usr/bin/mksquashfs'),
        Binaries.VERITYSETUP: _check_for_binary('/usr/bin/veritysetup'),
        Binaries.TAR: _check_for_binary('/usr/bin/tar'),
        })


def preflight_check(ctx: Context) -> None:
    """Run a fast pre-flight check on the context."""
    h2('Running Preflight Checks.', verbosity=2)

    _find_binaries(ctx)

    binaries = _preflight_binaries_check(ctx)
    users = _preflight_users_check(ctx)

    if not binaries or not users:
        raise PreflightError('Preflight Check failed.')


def _preflight_binaries_check(ctx: Context) -> bool:
    """Check executables."""
    passed = True
    for b in ctx._binaries.items():
        if b[1]:
            info('{} found: {}...'.format(b[0], b[1]))
        else:
            warn('{} not found.'.format(b[0]))
            passed = False
    return passed


def _preflight_users_check(ctx: Context) -> bool:
    """Check tha the script is running as root."""
    if os.geteuid() == 0:
        debug('Running as root.')
        return True
    warn('Not running as root.')
    return False
