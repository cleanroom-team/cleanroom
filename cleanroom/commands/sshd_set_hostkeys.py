# -*- coding: utf-8 -*-
"""sshd_set_hostkeys command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex

import cleanroom.helper.generic.file as file

import os.path
import glob


class SshdSetHostkeysCommand(cmd.Command):
    """The sshd_set_hostkeys command."""

    def __init__(self):
        """Constructor."""
        super().__init__('sshd_set_hostkeys', syntax='<HOSTKEY_DIR>)',
                         help='Install all the ssh_host_key* files found in '
                         '<HOSTKEY_DIR> for SSHD.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_arguments_exact(location, 1,
                                       '"{}" needs a directory with '
                                       'host keys.', *args)

        self._validate_keydir(args[0])
        return None

    def _validate_keydir(self, keydir):
        if not os.path.isdir(keydir):
            raise ex.ParseError('"{}": {} must be a directory.'
                                .format(self.name(), keydir))

        keyfiles = glob(os.path.join(keydir, 'ssh_host_key*'))
        if not keyfiles:
            raise ex.ParseError('"{}": No ssh_host_key files found in {}.'
                                .format(self.name(), keydir))

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        keydir = args[0]
        self._validate_keydir(keydir)
        if not file.isdir(system_context, '/etc/ssh'):
            raise ex.GenerateError(location,
                                   '"{}": No /etc/ssh directory found '
                                   'in system.'.format(self.name()))

        system_context.execute(location, 'copy', keydir + '/ssh_host_keys*',
                               '/etc/ssh', from_outside=True)
        file.chown(system_context, 'root', 'root',
                   '/etc/ssh/ssh_host_keys*')
        file.chmod(system_context, 0o600, '/etc/ssh/ssh_host_keys*')
        file.chmod(system_context, 0o644, '/etc/ssh/ssh_host_keys*.pub')
