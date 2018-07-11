# -*- coding: utf-8 -*-
"""_setup command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.context import Binaries

from cleanroom.helper.btrfs import create_subvolume

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
        self._setup_var_lib_directory(location, system_context, 'machines')
        self._setup_var_lib_directory(location, system_context, 'portables')

    def _setup_current_system_directory(self, system_context):
        create_subvolume(system_context.current_system_directory(),
                         command=system_context.binary(Binaries.BTRFS))
        os.makedirs(system_context.fs_directory())
        os.makedirs(system_context.boot_data_directory())
        os.makedirs(system_context.meta_directory())

    def _setup_var_lib_directory(self, location, system_context, dir):
        todo_dir = os.path.join('/var/lib', dir)
        system_context.execute(location,
                               'mkdir', todo_dir, mode=0o700, user='root', group='root')
