# -*- coding: utf-8 -*-
"""pkg_gnome command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class PkgGnomeCommand(Command):
    """The pkg_gnome command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__('pkg_gnome',
                         help_string='Install the Gnome desktop environment',
                         file=__file__, **services)

    def validate(self, location: Location,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        self._execute(location, system_context,
                      'pacman', '--assume-installed', 'jack',
                      'baobab', 'brasero', 'cheese', 'chrome-gnome-shell',
                      'file-roller', 'p7zip', 'unrar', 'unace', 'lrzip',
                      'gdm', 'gnome-color-manager', 'gnome-control-center',
                      'gnome-keyring', 'gnome-menus', 'gnome-screenshot',
                      'gnome-shell', 'gnome-shell-extensions',
                      'gnome-system-monitor', 'gnome-terminal',
                      'gnome-tweaks', 'gvfs', 'gvfs-afc', 'gvfs-goa',
                      'gvfs-google', 'gvfs-gphoto2', 'gvfs-mtp',
                      'gvfs-smb', 'mousetweaks', 'nautilus',
                      'networkmanager', 'networkmanager-openvpn',
                      'networkmanager-vpnc', 'pavucontrol',
                      'sane', 'sound-juicer', 'tracker-miners',
                      'usb_modeswitch', 'xdg-user-dirs-gtk',
                      'xorg-server-xwayland',)

        location.set_description('networkmanager fixup')
        self._execute(location.next_line(), system_context, 'create',
                      '/usr/lib/tmpfiles.d/networkmanager.conf',
                      '''d /var/lib/NetworkManager 0700 root root
d /var/lib/NetworkManager/system-connections 0750 root root
''', mode=0o644)

        self._execute(location.next_line(), system_context,
                      'systemd_enable', 'NetworkManager.service',
                      'NetworkManager-dispatcher.service')
#        self._execute(location.next_line(), system_context, 'remove',
#                      '/usr/lib/systemd/system/'
#                      'dbus-org.freedesktop.nm-dispatcher.service',
#                      '/usr/lib/systemd/system/'
#                      dbus-org.freedesktop.NetworkManager.service')
        self._execute(location.next_line(), system_context, 'symlink',
                      'NetworkManager.service',
                      'dbus-org.freedesktop.NetworkManager.service',
                      work_directory='/usr/lib/systemd/system')
        self._execute(location.next_line(), system_context, 'symlink',
                      'NetworkManager-dispatcher.service',
                      'dbus-org.freedesktop.nm-dispatcher.service',
                      work_directory='/usr/lib/systemd/system')

        self._execute(location.next_line(), system_context, 'mkdir',
                      '/var/lib/NetworkManager/system-connections')
        self._execute(location.next_line(), system_context, 'remove',
                      '/etc/NetworkManager/system-connections',
                      recursive=True, force=True)
        self._execute(location.next_line(), system_context, 'symlink',
                      '../../var/lib/NetworkManager/system-connections',
                      'system-connections',
                      work_directory='/etc/NetworkManager')
        self._add_hook(location.next_line(), system_context,
                       'export', 'remove', '/usr/share/gtk-doc/html/*',
                       recursive=True, force=True)

        self._execute(location.next_line(), system_context,
                      'systemd_enable', 'gdm.service')

        # FS#63706: Make sure gdm account is not expired!
        # self._execute(location.next_line(), system_context,
        #               'sed', '/account/ caccount required pam_permit.so',
        #               '/etc/pam.d/gdm-launch-environment')
        # self._execute(location.next_line(), system_context,
        #               'sed', 's/#Enable=true/Enable=true/', '/etc/gdm/custom.conf')
        # self._execute(location.next_line(), system_context,
        #               'sed', '/account/ caccount required pam_permit.so',
        #               '/etc/pam.d/systemd-user')
        self._execute(location.next_line(), system_context,
                      'run', '/usr/bin/chage', '-E', '-1', 'gdm', inside=True)
        # END FS#63706
