# -*- coding: utf-8 -*-
"""group manipulation commands.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


def groupadd(system_context, group_name, *, gid=-1, force=False, system=False):
    """Execute command."""
    command = ['/usr/bin/groupadd', group_name]

    if gid >= 0:
        command += ['--gid', str(gid)]

    if force:
        command += ['--force']

    if system:
        command += ['--system']

    system_context.run(*command)
