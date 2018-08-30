# -*- coding: utf-8 -*-
"""sshd_install_knownhosts command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.file import (chmod, chown, isdir,)

from cleanroom.exceptions import (GenerateError, ParseError,)

import os.path
import glob


class SshdInstallKnownhostsCommand(Command):
    """The sshd_install_knownhosts command."""

    def __init__(self):
        """Constructor."""
        super().__init__('sshd_install_knownhosts',
                         help='Install system wide knownhosts file.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        key_directory = args[0]
        self._validate_key_directory(location, key_directory)
        if not isdir(system_context, '/etc/ssh'):
            raise GenerateError('"{}": No /etc/ssh directory found in system.'
                                .format(self.name()), location=location)

