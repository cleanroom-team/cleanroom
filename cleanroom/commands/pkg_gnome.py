# -*- coding: utf-8 -*-
"""pkg_gnome command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.helper.file import remove
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class PkgGnomeCommand(Command):
    """The pkg_gnome command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "pkg_gnome",
            help_string="Install the Gnome desktop environment",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

        return None

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        self._execute(
            location,
            system_context,
            "pacman",
            "--dbonly",
            "qt5-base",
            "qt5-declarative",
            "qt5-wayland",
            "qt5-x11extras",
        )
        self._execute(
            location,
            system_context,
            "pacman",
            "pipewire",
            "pipewire-alsa",
            "pipewire-pulse",
            "pipewire-jack",
            "baobab",
            "brasero",
            "cheese",
            "file-roller",
            "p7zip",
            "unrar",
            "unace",
            "lrzip",
            "gdm",
            "gnome-color-manager",
            "gnome-control-center",
            "gnome-keyring",
            "gnome-menus",
            "gnome-screenshot",
            "gnome-shell",
            "gnome-shell-extensions",
            "gnome-system-monitor",
            "gnome-terminal",
            "gnome-tweaks",
            "gvfs",
            "gvfs-afc",
            "gvfs-goa",
            "gvfs-google",
            "gvfs-gphoto2",
            "gvfs-mtp",
            "gvfs-smb",
            "mousetweaks",
            "nautilus",
            "networkmanager",
            "networkmanager-openvpn",
            "networkmanager-vpnc",
            "pavucontrol",
            "sane",
            "sound-juicer",
            "tracker3-miners",
            "usb_modeswitch",
            "xdg-user-dirs-gtk",
            "xorg-server-xwayland",
            "gnome-remote-desktop",
            "gnome-user-share",
            "rygel",
            "system-config-printer",
        )

        location.set_description("networkmanager fixup")
        self._execute(
            location.next_line(),
            system_context,
            "create",
            "/usr/lib/tmpfiles.d/networkmanager.conf",
            """d /var/etc/NetworkManager 0700 root root
d /var/etc/NetworkManager/system-connections 0750 root root
""",
            mode=0o644,
        )

        self._execute(
            location.next_line(),
            system_context,
            "systemd_enable",
            "NetworkManager.service",
            "NetworkManager-dispatcher.service",
        )
        #        self._execute(location.next_line(), system_context, 'remove',
        #                      '/usr/lib/systemd/system/'
        #                      'dbus-org.freedesktop.nm-dispatcher.service',
        #                      '/usr/lib/systemd/system/'
        #                      dbus-org.freedesktop.NetworkManager.service')
        self._execute(
            location.next_line(),
            system_context,
            "symlink",
            "NetworkManager.service",
            "dbus-org.freedesktop.NetworkManager.service",
            work_directory="/usr/lib/systemd/system",
        )
        self._execute(
            location.next_line(),
            system_context,
            "symlink",
            "NetworkManager-dispatcher.service",
            "dbus-org.freedesktop.nm-dispatcher.service",
            work_directory="/usr/lib/systemd/system",
        )

        self._execute(
            location.next_line(),
            system_context,
            "mkdir",
            "/var/etc/NetworkManager/system-connections",
        )
        self._execute(
            location.next_line(),
            system_context,
            "remove",
            "/etc/NetworkManager/system-connections",
            recursive=True,
            force=True,
        )
        self._execute(
            location.next_line(),
            system_context,
            "symlink",
            "../../var/etc/NetworkManager/system-connections",
            "system-connections",
            work_directory="/etc/NetworkManager",
        )
        self._add_hook(
            location.next_line(),
            system_context,
            "export",
            "remove",
            "/usr/share/gtk-doc/html/*",
            recursive=True,
            force=True,
        )

        self._execute(
            location.next_line(), system_context, "systemd_enable", "gdm.service"
        )
