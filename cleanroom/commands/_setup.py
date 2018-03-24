# -*- coding: utf-8 -*-
"""_setup command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.helper.generic.btrfs as btrfs

import os
import stat


class _SetupCommand(cmd.Command):
    """The _setup Command."""

    def __init__(self):
        """Constructor."""
        super().__init__('_setup',
                         help='Implicitly run before any '
                         'other command of a system is run.')

    def validate_arguments(self, location, *args, **kwargs):
        return self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        self._setup_current_system_directory(system_context)

        # Make sure systemd does not create /var/lib/machines for us!
        self._setup_var_lib_machines(location, system_context)

        self._setup_testing_hook(location, system_context)

    def _setup_current_system_directory(self, system_context):
        btrfs.create_subvolume(system_context,
                               system_context.ctx.current_system_directory())
        os.makedirs(system_context.fs_directory())
        os.makedirs(system_context.meta_directory())

    def _setup_var_lib_machines(self, location, system_context):
        machines_dir = '/var/lib/machines'
        system_context.execute(location, 'mkdir', machines_dir,
                               mode=(stat.S_IRUSR | stat.S_IWUSR
                                     | stat.S_IXUSR),
                               user='root', group='root')

    def _setup_testing_hook(self, location, system_context):
        test_flag = 'testing_was_set_up'
        if not system_context.flags.get(test_flag, False):
            location.next_line_offset('testing')
            system_context.add_hook('_test', location, '_test')
            system_context.flags[test_flag] = True
