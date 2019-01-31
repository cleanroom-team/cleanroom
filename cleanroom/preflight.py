# -*- coding: utf-8 -*-
"""The Context the generation will run in.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .exceptions import PreflightError
from .printer import debug, fail, h2, success, warn

import os
import typing


def preflight_check(title: str,
                    func: typing.Callable[[], None], *,
                    ignore_errors=False) -> None:
    try:
        func()
    except PreflightError:
        fail('Preflight Check "{}" failed'.format(title),
             ignore=ignore_errors)
        if not ignore_errors:
            raise
    else:
        success('Preflight Check "{}" passed'.format(title),
                verbosity=2)


def users_check() -> None:
    """Check tha the script is running as root."""
    if os.geteuid() == 0:
        debug('Running as root.')
        return True
    raise PreflightError('Not running as user "root".')
