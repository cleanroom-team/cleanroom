# -*- coding: utf-8 -*-
"""ssh_allow_login command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.file import (chmod, chown, exists, isdir, read_file,)
from cleanroom.generator.helper.generic.user import user_data

from cleanroom.exceptions import GenerateError

import os.path


class SshAllowLoginCommand(Command):
    """The ssh_allow_login command."""

    def __init__(self):
        """Constructor."""
        super().__init__('ssh_allow_login', syntax='<USER> <PUBLIC_KEYFILE> '
                         'optins=<OPTIONS>',
                         help='Authorize <PUBLIC_KEYFILE> to log in '
                         'as <USER>.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_exact(location, 2, '"{}" needs a user and '
                                  'a public keyfile.', *args)
        self._validate_kwargs(location, ('options'), **kwargs)

    def _check_or_create_directory(self, location, system_context, dir,
                                   **kwargs):
        if not exists(system_context, dir):
            system_context.execute(location, 'mkdir', dir, **kwargs)
            return
        if not isdir(system_context, dir):
            raise GenerateError('"{}" needs directory "{}", but that exists and '
                                'is not a directory.'.format(self.name(), dir),
                                location=location)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        user = args[0]
        keyfile = args[1]

        user = user_data(system_context, user)
        if user is None:
            raise GenerateError('"{}" could not find user "{}".'
                                .format(self.name(), user),
                                location=location)

        self._check_or_create_directory(location, system_context, user.home,
                                        mode=0o750, user=user.uid, group=user.gid)
        ssh_directory = os.path.join(user.home, '.ssh')
        self._check_or_create_directory(location, system_context, ssh_directory,
                                        mode=0o600, user=user.uid, group=user.gid)

        key = read_file(system_context, keyfile, outside=True).decode('utf-8')

        authorized_file = os.path.join(ssh_directory, 'authorized_keys')
        line = ''

        options = kwargs.get('options', '')

        if options:
            line = options + ' ' + key + '\n'
        else:
            line += key + '\n'

        system_context.execute(location, 'append', authorized_file, line,
                               force=True)
        chown(system_context, user.uid, user.gid, authorized_file)
        chmod(system_context, 0o644, authorized_file)
