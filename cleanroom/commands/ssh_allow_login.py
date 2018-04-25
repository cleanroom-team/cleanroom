# -*- coding: utf-8 -*-
"""ssh_allow_login command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex

import cleanroom.helper.generic.file as file
import cleanroom.helper.generic.user as userdb

import os.path


class SshAllowLoginCommand(cmd.Command):
    """The ssh_allow_login command."""

    def __init__(self):
        """Constructor."""
        super().__init__('ssh_allow_login', syntax='<USER> <PUBLIC_KEYFILE> '
                         'optins=<OPTIONS>',
                         help='Authorize <PUBLIC_KEYFILE> to log in '
                         'as <USER>.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_exact(location, 2, '"{}" needs a user and '
                                  'a public keyfile.', *args)
        return self._validate_kwargs(location, ('options'), **kwargs)

    def _check_or_create_directory(self, location, system_context, dir,
                                   **kwargs):
        if not file.exists(system_context, dir):
            system_context.execute(location, 'mkdir', dir, **kwargs)
            return
        if not file.isdir(system_context, dir):
            raise ex.GenerateError(location, '"{}" needs directory "{}", but '
                                   'that exists and is not a directory.'
                                   .format(self.name(), dir))

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        user = args[0]
        keyfile = args[1]

        user_data = userdb.user_data(system_context, user)
        if user_data is None:
            raise ex.GenerateError(location, '"{}" could not find user "{}".'
                                   .format(self.name(), user))

        self._check_or_create_directory(location, system_context,
                                        user_data.home,
                                        mode=0o750, user=user_data.uid,
                                        group=user_data.gid)
        ssh_directory = os.path.join(user_data.home, '.ssh')
        self._check_or_create_directory(location, system_context,
                                        ssh_directory,
                                        mode=0o600, user=user_data.uid,
                                        group=user_data.gid)

        key = file.read_file(system_context, keyfile, outside=True)

        authorized_file = os.path.join(ssh_directory, 'authorized_keys')
        line = ''

        options = kwargs.get('options', '')

        if options:
            line = options + ' ' + key + '\n'
        else:
            line += key + '\n'

        system_context.execute(location, 'append', authorized_file, line)
        file.chown(system_context, user_data.uid, user_data.gid,
                   authorized_file)
        file.chmod(system_context, 0o644, authorized_file)
