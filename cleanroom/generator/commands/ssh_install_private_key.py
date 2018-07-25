# -*- coding: utf-8 -*-
"""ssh_install_private_key command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.file import (chmod, chown, exists, isdir, makedirs,)
from cleanroom.generator.helper.generic.user import user_data

import cleanroom.exceptions as ex
from cleanroom.printer import (debug, trace,)

import os.path


class SshInstallPrivateKeyCommand(Command):
    """The ssh_install_private_key command."""

    def __init__(self):
        """Constructor."""
        super().__init__('ssh_install_private_key', syntax='<USER> <KEYFILE>',
                         help='Install <KEYFILE> as private key for <USER>.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_arguments_exact(location, 2,
                                       '"{}" needs a user and a keyfile.',
                                       *args, **kwargs)

    def _check_or_create_directory(self, location, system_context, dir,
                                   **kwargs):
        if not exists(system_context, dir):
            makedirs(system_context, dir, **kwargs)
            return
        if not isdir(system_context, dir):
            raise ex.GenerateError('"{}" needs directory "{}", but '
                                   'that exists and is not a directory.'
                                   .format(self.name(), dir),
                                   location=location)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        user_name = args[0]
        key_file = args[1]

        location

        user = user_data(system_context, user_name)
        if user is None:
            raise ex.GenerateError('"{}" could not find user "{}".'
                                   .format(self.name(), user_name),
                                   location=location)

        debug('Installing "{}" to user "{}" ({}).'.format(key_file, user_name, user.home))

        self._check_or_create_directory(location, system_context, user.home,
                                        mode=0o750, user=user.uid, group=user.gid)
        ssh_directory = os.path.join(user.home, '.ssh')
        self._check_or_create_directory(location, system_context,
                                        ssh_directory,
                                        mode=0o600, user=user.uid, group=user.gid)

        installed_key_file = os.path.join(ssh_directory, os.path.basename(key_file))

        system_context.execute(location.next_line(), 'copy', key_file,
                               installed_key_file, from_outside=True)
        trace('Copied key.')
        chown(system_context, user.uid, user.gid, installed_key_file)
        trace('Ownership adjusted.')
        chmod(system_context, 0o600, installed_key_file)
        trace('Mode adjusted.')
