# -*- coding: utf-8 -*-
"""Helpers for systemd inteaction.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


def systemd_enable(system_context, *services, **kwargs):
    """Enable systemd service."""
    all_args = ['--root={}'.format(system_context.fs_directory()),]
    if kwargs.get('user', False):
        all_args += ['--global']
    all_args += ['enable',]
    system_context.run('/usr/bin/systemctl',
                       *all_args, *services, outside=True)
