# -*- coding: utf-8 -*-
"""_setup command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.context import Binaries
from cleanroom.generator.workdir import create_work_directory

from cleanroom.helper.run import run

import os
import stat


class _SetupCommand(Command):
    """The _setup Command."""

    def __init__(self):
        """Constructor."""
        super().__init__('_setup',
                         help='Implicitly run before any '
                         'other command of a system is run.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        self._setup_current_system_directory(system_context)

        # Make sure systemd does not create /var/lib/* for us!
        os.makedirs(system_context.file_name('/var/lib/machines'))
        os.makedirs(system_context.file_name('/var/lib/portables'))

    def _setup_current_system_directory(self, system_context):
        create_work_directory(system_context.ctx)

        # Make sure there is /dev/null in the filesystem:
        os.makedirs(system_context.file_name('/dev'))
        
        run('/usr/bin/mknod', '--mode=666',
            system_context.file_name('/dev/null'), 'c', '1', '3')
        run('/usr/bin/mknod', '--mode=666',
            system_context.file_name('/dev/zero'), 'c', '1', '5')
        run('/usr/bin/mknod', '--mode=666',
            system_context.file_name('/dev/random'), 'c', '1', '8')


