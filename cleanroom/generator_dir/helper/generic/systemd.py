# -*- coding: utf-8 -*-
"""Helpers for systemd inteaction.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from ...systemcontext import (SystemContext,)

import typing


def systemd_enable(system_context: SystemContext, *services: str,
                   **kwargs: typing.Any) -> None:
    """Enable systemd service."""
    all_args = ['--root={}'.format(system_context.fs_directory())]
    if kwargs.get('user', False):
        all_args.append('--global')
    all_args.append('enable')
    system_context.run('/usr/bin/systemctl',
                       *all_args, *services, outside=True)
