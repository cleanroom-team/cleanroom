# -*- coding: utf-8 -*-
"""The Context the generation will run in.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.exceptions as ex
import cleanroom.context as context
import cleanroom.printer as printer

import os


def _check_for_binary(binary):
    """Check for binaries (with full path!)."""
    return binary if os.access(binary, os.X_OK) else ''


def _find_binaries(ctx):
    ctx.set_binaries({
        context.Binaries.BORG: _check_for_binary('/usr/bin/borg'),
        context.Binaries.BTRFS: _check_for_binary('/usr/bin/btrfs'),
        context.Binaries.PACMAN: _check_for_binary('/usr/bin/pacman'),
        context.Binaries.PACMAN_KEY: _check_for_binary('/usr/bin/pacman-key'),
        context.Binaries.PACSTRAP: _check_for_binary('/usr/bin/pacstrap'),
        context.Binaries.SBSIGN: _check_for_binary('/usr/bin/sbsign'),
        })


def preflight_check(ctx):
    """Run a fast pre-flight check on the context."""
    printer.h2('Running Preflight Checks.', verbosity=2)

    _find_binaries(ctx)

    binaries = _preflight_binaries_check(ctx)
    users = _preflight_users_check(ctx)

    if not binaries or not users:
        raise ex.PreflightError('Preflight Check failed.')


def _preflight_binaries_check(ctx):
    """Check executables."""
    passed = True
    for b in ctx._binaries.items():
        if b[1]:
            printer.info('{} found: {}...'.format(b[0], b[1]))
        else:
            printer.warn('{} not found.'.format(b[0]))
            passed = False
    return passed


def _preflight_users_check(ctx):
    """Check tha the script is running as root."""
    if os.geteuid() == 0:
        printer.debug('Running as root.')
        return True
    printer.warn('Not running as root.')
    return False
