# -*- coding: utf-8 -*-
"""The Context the generation will run in.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .exceptions import PreflightError
from .printer import debug, h2, warn
from .binarymanager import BinaryManager

import os


def _preflight_users_check() -> bool:
    """Check tha the script is running as root."""
    if os.geteuid() == 0:
        debug('Running as root.')
        return True
    warn('Not running as root.')
    return False


def preflight_check(binary_manager: BinaryManager) -> None:
    """Run a fast pre-flight check on the context."""
    h2('Running Preflight Checks.', verbosity=2)

    binaries = binary_manager.preflight_check()
    users = _preflight_users_check()

    if not binaries or not users:
        raise PreflightError('Preflight Check failed.')
