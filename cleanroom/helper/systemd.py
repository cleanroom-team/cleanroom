# -*- coding: utf-8 -*-
"""Helpers for systemd inteaction.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from ..systemcontext import SystemContext
from .run import run

import typing


def systemd_enable(
    system_context: SystemContext,
    *services: str,
    systemctl_command: str,
    **kwargs: typing.Any,
) -> None:
    """Enable systemd service."""
    all_args = [
        f"--root={system_context.fs_directory}",
    ]
    if kwargs.get("user", False):
        all_args.append("--global")
    all_args.append("enable")
    run(systemctl_command, *all_args, *services)
