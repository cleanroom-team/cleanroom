"""_setup command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.helper.generic.file as file
import cleanroom.command as cmd

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
        # Make sure systemd does not create /var/lib/machines for us!
        machines_dir = '/var/lib/machines'
        file.makedirs(run_context, machines_dir,
                      mode=(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR),
                      user='root', group='root')

        test_flag = 'testing_was_set_up'
        if not run_context.flags.get(test_flag, False):
            run_context.add_hook('_test', '_test', message='testing',
                                 file_name=file_name, line_number=line_number)
            run_context.flags[test_flag] = True
