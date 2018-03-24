# -*- coding: utf-8 -*-
"""user commands.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


def useradd(run_context, user_name, *,
            comment='', home='', gid=-1, uid=-1, shell='',
            groups='', password='', expire=None):
    """Add a new user to the system."""
    command = ['/usr/bin/useradd', user_name]

    if comment:
        command += ['--comment', comment]

    if home:
        command += ['--home', home]

    if gid >= 0:
        command += ['--gid', str(gid)]

    if uid >= 0:
        command += ['--uid', str(uid)]

    if shell:
        command += ['--shell', shell]

    if groups:
        command += ['--groups', groups]

    if password:
        command += ['--password', password]

    if expire is not None:
        if expire == 'None':
            command.append('--expiredate')
        else:
            command += ['--expiredate', expire]

    run_context.run(*command)


def usermod(run_context, user_name, *, comment='', home='', gid=-1, uid=-1,
            lock=None, rename='', shell='', append=False, groups='',
            password='', expire=None):
    """Modify an existing user."""
    command = ['/usr/bin/usermod', user_name]

    if comment:
        command += ['--comment', comment]

    if home:
        command += ['--home', home]

    if gid >= 0:
        command += ['--gid', str(gid)]

    if uid >= 0:
        command += ['--uid', str(uid)]

    if lock is not None:
        if lock:
            command.append('--lock')
        elif not lock:
            command.append('--unlock')

    if expire is not None:
        if expire == 'None':
            command.append('--expiredate')
        else:
            command += ['--expiredate', expire]

    if shell:
        command += ['--shell', shell]

    if rename:
        command += ['--login', rename]

    if append:
        command.append('--append')

    if groups:
        command += ['--groups', groups]

    if password:
        command += ['--password', password]

    if expire is not None:
        command += ['--expiredate', expire]

    run_context.run(*command)
