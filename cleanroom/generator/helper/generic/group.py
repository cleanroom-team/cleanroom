# -*- coding: utf-8 -*-
"""group manipulation commands.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import collections
import os.path


Group = collections.namedtuple('Group', ['name', 'password', 'gid', 'members'])


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


def _group_data(group_file, name):
    if not os.path.exists(group_file):
        return None

    with open(group_file, 'r') as group:
        for line in group:
            if line.endswith('\n'):
                line = line[:-1]
            current_group = line.split(':')
            if current_group[0] == name:
                print('XXX:{}:XXX'.format(current_group[3]))
                current_group[2] = int(current_group[2])
                if current_group[3] == '':
                    current_group[3] = []
                else:
                    current_group[3] = list(current_group[3].split(','))
                return Group(*current_group)
    return Group('nobody', 'x', 65534, [])


def group_data(system_context, name):
    """Get user data from passwd file."""
    return _group_data(system_context.file_name('/etc/group'), name)
