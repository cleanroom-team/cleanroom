# -*- coding: utf-8 -*-
"""sshd_set_hostkeys command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.file import (chmod, chown, isdir,)

from cleanroom.exceptions import (GenerateError, ParseError,)

import os.path
import glob


class SshdSetHostkeysCommand(Command):
    """The sshd_set_hostkeys command."""

    def __init__(self):
        """Constructor."""
        super().__init__('sshd_set_hostkeys', syntax='<HOSTKEY_DIR>)',
                         help='Install all the ssh_host_*_key files found in '
                         '<HOSTKEY_DIR> for SSHD.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_arguments_exact(location, 1,
                                       '"{}" needs a directory with '
                                       'host keys.', *args)

    def _key_files(self, key_directory):
        return os.path.join(key_directory, 'ssh_host_*_key*')

    def _validate_key_directory(self, location, key_directory):
        if not os.path.isdir(key_directory):
            raise ParseError('"{}": {} must be a directory (work directory is {}).'
                             .format(self.name(), key_directory, os.getcwd()))

        keyfiles = glob.glob(self._key_files(key_directory))
        if not keyfiles:
            raise ParseError('"{}": No ssh_host_*_key files found in {}.'
                             .format(self.name(), key_directory),
                             location=location)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        key_directory = args[0]
        self._validate_key_directory(location, key_directory)
        if not isdir(system_context, '/etc/ssh'):
            raise GenerateError('"{}": No /etc/ssh directory found in system.'
                                .format(self.name()), location=location)

        system_context.execute(location.next_line(),
                               'copy', self._key_files(key_directory),
                               '/etc/ssh', from_outside=True)
        chown(system_context, 'root', 'root', self._key_files('/etc/ssh'))
        chmod(system_context, 0o600, '/etc/ssh/ssh_host_*_key')
        chmod(system_context, 0o644, '/etc/ssh/ssh_host_*_key.pub')
