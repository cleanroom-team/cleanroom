"""_setup command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.helper.generic.btrfs as btrfs
import cleanroom.helper.generic.file as file

import os
import stat


class _SetupCommand(cmd.Command):
    """The _setup Command."""

    def __init__(self):
        """Constructor."""
        super().__init__("_setup",
                         "Implicitly run before any other command of a "
                         "system is run.")

    def __call__(self, file_name, line_number, run_context, *args, **kwargs):
        """Execute command."""
        self._setup_current_system_directory(run_context)

        # Make sure systemd does not create /var/lib/machines for us!
        self._setup_var_lib_machines(run_context)

        self._setup_testing_hook(run_context,
                                 file_name=file_name, line_number=line_number)

    def _setup_current_system_directory(self, run_context):
        btrfs.create_subvolume(run_context,
                               run_context.current_system_directory())
        os.makedirs(run_context.fs_directory())
        os.makedirs(run_context.meta_directory())

    def _setup_var_lib_machines(self, run_context):
        machines_dir = '/var/lib/machines'
        file.makedirs(run_context, machines_dir,
                      mode=(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR),
                      user='root', group='root')

    def _setup_testing_hook(self, run_context, *,
                            file_name='', line_number=-1):
        test_flag = 'testing_was_set_up'
        if not run_context.flags.get(test_flag, False):
            run_context.add_hook('_test', '_test', message='testing',
                                 file_name=file_name, line_number=line_number)
            run_context.flags[test_flag] = True
