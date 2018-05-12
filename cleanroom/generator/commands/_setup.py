# -*- coding: utf-8 -*-
"""_setup command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.btrfs import create_subvolume

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

        # Make sure systemd does not create /var/lib/machines for us!
        self._setup_var_lib_machines(location, system_context)

    def _setup_current_system_directory(self, system_context):
        create_subvolume(system_context, system_context.ctx.current_system_directory())
        os.makedirs(system_context.fs_directory())
        os.makedirs(system_context.boot_data_directory())
        os.makedirs(system_context.meta_directory())

    def _setup_var_lib_machines(self, location, system_context):
        machines_dir = '/var/lib/machines'
        system_context.execute(location, 'mkdir', machines_dir,
                               mode=(stat.S_IRUSR | stat.S_IWUSR
                                     | stat.S_IXUSR),
                               user='root', group='root')
