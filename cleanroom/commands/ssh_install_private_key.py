# -*- coding: utf-8 -*-
"""ssh_install_private_key command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.printer as printer

import cleanroom.helper.generic.file as file
import cleanroom.helper.generic.user as userdb

import os.path


class SshInstallPrivateKeyCommand(cmd.Command):
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
        if not file.exists(system_context, dir):
            system_context.execute(location, 'mkdir', dir, **kwargs)
            return
        if not file.isdir(system_context, dir):
            raise ex.GenerateError('"{}" needs directory "{}", but '
                                   'that exists and is not a directory.'
                                   .format(self.name(), dir),
                                   location=location)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        user = args[0]
        keyfile = args[1]

        user_data = userdb.user_data(system_context, user)
        if user_data is None:
            raise ex.GenerateError('"{}" could not find user "{}".'
                                   .format(self.name(), user),
                                   location=location)

        printer.verbose('Installing "{}" to user "{}" ({}).'
                        .format(keyfile, user, user_data.home))

        self._check_or_create_directory(location, system_context,
                                        user_data.home,
                                        mode=0o750, user=user_data.uid,
                                        group=user_data.gid)
        ssh_directory = os.path.join(user_data.home, '.ssh')
        self._check_or_create_directory(location, system_context,
                                        ssh_directory,
                                        mode=0o600, user=user_data.uid,
                                        group=user_data.gid)

        installed_keyfile = os.path.join(ssh_directory,
                                         os.path.basename(keyfile))

        system_context.execute(location, 'copy', keyfile,
                               installed_keyfile, from_outside=True)
        printer.trace('Copied key.')
        file.chown(system_context, user_data.uid, user_data.gid,
                   installed_keyfile)
        printer.trace('Ownership adjusted.')
        file.chmod(system_context, 0o600, installed_keyfile)
        printer.trace('Mode adjusted.')
