# -*- coding: utf-8 -*-
"""setup_readonly_usr command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd


class SetupReadonlyUsrCommand(cmd.Command):
    """The setup_readonly_usr command."""

    def __init__(self):
        """Constructor."""
        super().__init__('setup_readonly_usr',
                         help='Set up system for a read-only /usr partition.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        return self._validate_no_arguments(location, *args, **kwargs)

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

        # Remove unnecessary tmpfiles.d:
        system_context.execute(location,
                               'remove', '/usr/lib/tmpfiles.d/man-db.conf')

        # Remove arch.conf tmpfiles.d:
        system_context.execute(location,
                               'remove', '/usr/share/factory/etc/crypttab',
                               '/usr/share/factory/etc/fstab',
                               '/usr/share/factory/etc/group',
                               '/usr/share/factory/etc/gshadow',
                               '/usr/share/factory/etc/host.conf',
                               '/usr/share/factory/etc/hosts',
                               '/usr/share/factory/etc/issue',
                               '/usr/share/factory/etc/ld.so.conf',
                               '/usr/share/factory/etc/motd',
                               '/usr/share/factory/etc/nsswitch.conf',
                               '/usr/share/factory/etc/passwd',
                               '/usr/share/factory/etc/profile',
                               '/usr/share/factory/etc/securetty',
                               '/usr/share/factory/etc/shadow',
                               '/usr/share/factory/etc/shells',
                               '/usr/lib/tmpfiles.d/arch.conf')

        # Remove firstboot:
        system_context.execute(location, 'remove',
                               '/usr/lib/systemd/system/sysinit.target.wants/'
                               'systemd-firstboot.service',
                               '/usr/lib/systemd/system/'
                               'systemd-firstboot.service',
                               '/usr/bin/systemd-firstboot')

        # Remove unnecessary systemd-timers:
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
        location.next_line_offset('Remove kernel-install')
        system_context.add_hook(location, 'export',
                                'remove', '/usr/lib/kernel', '/etc/kernel',
                                '/usr/bin/kernel-install',
                                recursive=True, force=True)
        location.next_line_offset('Run ldconfig')
        system_context.add_hook(location, 'export',
                                'run', '/usr/bin/ldconfig', '-X')
        location.next_line_offset('Remove ldconfig data')
        system_context.add_hook(location, 'export',
                                'remove', '/usr/bin/ldconfig')
        location.next_line_offset('Update HWDB')
        system_context.add_hook(location, 'export',
                                'run',
                                '/usr/bin/systemd-hwdb', '--usr', 'update')
        location.next_line_offset('Remove HWDB data')
        system_context.add_hook(location, 'export',
                                'remove', '/usr/bin/systemd-hwdb')

        # Shell cleanup:
        location.next_line_offset('Clear ZSH files')
        system_context.add_hook(location, '_teardown', 'run',
                                'test', '-x', '/usr/bin/zsh',
                                '&&', 'rm', '-rf', '/usr/share/zsh', shell=True)
