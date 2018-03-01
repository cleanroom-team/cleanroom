"""setup_readonly_usr command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file


class SetupReadonlyUsrCommand(cmd.Command):
    """The setup_readonly_usr command."""

    def __init__(self):
        """Constructor."""
        super().__init__('setup_readon-y_usr',
                         'Set up system for a read-only /usr partition.')

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 0:
            raise ex.ParseError('setup_readonly_usr does not take any '
                                'argument.',
                                file_name=file_name, line_number=line_number)

        return None

    def __call__(self, file_name, line_number, run_context, *args, **kwargs):
        """Execute command."""
        # Remove unnecessary systemd-generators:
        # Must keep fstab and cryptsetup generator for mkinitcpio
        file.remove(run_context,
                    '/usr/lib/systemd-generators/'
                    'systemd-system-update_generator')

        # # Remove unnecessary systemd-timers:
        file.remove(run_context,
                    '/usr/lib/systemd/system/timers.target.wants/shadow.timer')

        # Remove unnecessary systemd-services:
        file.remove(run_context,
                    '/usr/lib/systemd/system/*/ldconfig.service',
                    '/usr/lib/systemd/system/ldconfig.service',
                    '/usr/lib/systemd/system/*/systemd-hwdb-update.service',
                    '/usr/lib/systemd/system/systemd-hwdb-update.service)')

        # Things to update/clean on export:
        run_context.add_hook('export', 'run', '/usr/bin/ldconfig', '-X',
                             message='Run ldconfig',
                             file_name='<setup_readonly_usr>',
                             line_number=1)
        run_context.add_hook('export', 'remove', '/usr/bin/ldconfig',
                             message='Remove ldconfig data',
                             file_name='<setup_readonly_usr>',
                             line_number=2)
        run_context.add_hook('export',
                             'run', '/usr/bin/systemd-hwdb', '--usr', 'update',
                             message='Update HWDB',
                             file_name='<setup_readonly_usr>',
                             line_number=3)
        run_context.add_hook('export', 'remove', '/usr/bin/systemd-hwdb',
                             message='Remove HWDB data',
                             file_name='<setup_readonly_usr>',
                             line_number=4)
