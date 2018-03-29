# -*- coding: utf-8 -*-
"""Helpers for systemd inteaction.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


def systemd_enable(system_context, *services):
    """Enable systemd service."""
    system_context.run('/usr/bin/systemctl',
                       '--root={}'.format(system_context.fs_directory()),
                       'enable', *services, outside=True)
