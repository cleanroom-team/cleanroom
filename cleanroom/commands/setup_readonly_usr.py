# -*- coding: utf-8 -*-
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
                         help='Set up system for a read-only /usr partition.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 0:
            raise ex.ParseError('setup_readonly_usr does not take any '
                                'argument.', location=location)
        return None

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        # Remove files:
        system_context.execute(location,
                               'remove', '/etc/machine-id', '/usr/bin/init',
                               force=True)

        # Remove unnecessary systemd-generators:
        # Must keep fstab and cryptsetup generator for mkinitcpio
        system_context.execute(location,
                               'remove', '/usr/lib/systemd-generators/'
                               'systemd-system-update_generator')

        # # Remove unnecessary systemd-timers:
        system_context.execute(location, 'remove',
                               '/usr/lib/systemd/system/timers.target.wants/'
                               'shadow.timer')

        # Remove unnecessary systemd-services:
        system_context.execute(location, 'remove',
                               '/usr/lib/systemd/system/*/ldconfig.service',
                               '/usr/lib/systemd/system/ldconfig.service',
                               '/usr/lib/systemd/system/*/'
                               'systemd-hwdb-update.service',
                               '/usr/lib/systemd/system/'
                               'systemd-hwdb-update.service')

        # Things to update/clean on export:
        location.next_line_offset('Run ldconfig')
        system_context.add_hook('export', location,
                                'run', '/usr/bin/ldconfig', '-X')
        location.next_line_offset('Remove ldconfig data')
        system_context.add_hook('export', location,
                                'remove', '/usr/bin/ldconfig')
        location.next_line_offset('Update HWDB')
        system_context.add_hook('export', location,
                                'run',
                                '/usr/bin/systemd-hwdb', '--usr', 'update')
        location.next_line_offset('Remove HWDB data')
        system_context.add_hook('export', location,
                                'remove', '/usr/bin/systemd-hwdb')
