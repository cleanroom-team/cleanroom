# -*- coding: utf-8 -*-
"""Helpers for systemd inteaction.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


def systemd_enable(run_context, *services):
    """Enable systemd service."""
    run_context.run('/usr/bin/systemctl',
                    '--root={}'.format(run_context.fs_directory()),
                    'enable', *services, outside=True)
