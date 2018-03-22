"""setup_readonly_usr command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex


class SetupReadonlyUsrCommand(cmd.Command):
    """The setup_readonly_usr command."""

    def __init__(self):
        """Constructor."""
        super().__init__('setup_readonly_usr',
                         'Set up system for a read-only /usr partition.')

    def validate_arguments(self, run_context, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 0:
            raise ex.ParseError('setup_readonly_usr does not take any '
                                'argument.', run_context=run_context)
        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        # Remove files:
        run_context.execute('remove', '/etc/machine-id', '/usr/bin/init',
                            force=True)

        # Remove unnecessary systemd-generators:
        # Must keep fstab and cryptsetup generator for mkinitcpio
        run_context.execute('remove', '/usr/lib/systemd-generators/'
                            'systemd-system-update_generator')

        # # Remove unnecessary systemd-timers:
        run_context.execute('remove',
                            '/usr/lib/systemd/system/timers.target.wants/'
                            'shadow.timer')

        # Remove unnecessary systemd-services:
        run_context.execute('remove',
                            '/usr/lib/systemd/system/*/ldconfig.service',
                            '/usr/lib/systemd/system/ldconfig.service',
                            '/usr/lib/systemd/system/*/'
                            'systemd-hwdb-update.service',
                            '/usr/lib/systemd/system/'
                            'systemd-hwdb-update.service')

        # Things to update/clean on export:
        run_context.add_hook('export', 'run', '/usr/bin/ldconfig', '-X',
                             message='Run ldconfig')
        run_context.add_hook('export', 'remove', '/usr/bin/ldconfig',
                             message='Remove ldconfig data')
        run_context.add_hook('export',
                             'run', '/usr/bin/systemd-hwdb', '--usr', 'update',
                             message='Update HWDB')
        run_context.add_hook('export', 'remove', '/usr/bin/systemd-hwdb',
                             message='Remove HWDB data')
