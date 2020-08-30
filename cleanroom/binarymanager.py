# -*- coding: utf-8 -*-
"""An object used to find/get host system binaries.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .exceptions import PreflightError
from .printer import debug, fail, trace, warn

from enum import Enum, auto, unique
import os
import typing


@unique
class Binaries(Enum):
    """Important binaries."""

    APT_GET = auto()
    BORG = auto()
    BTRFS = auto()
    CHROOT_HELPER = auto()
    DEBOOTSTRAP = auto()
    DEPMOD = auto()
    DPKG = auto()
    FIND = auto()
    FLOCK = auto()
    GROUPADD = auto()
    GROUPMOD = auto()
    MKFS_VFAT = auto()
    MKNOD = auto()
    MKSQUASHFS = auto()
    MODPROBE = auto()
    NBD_CLIENT = auto()
    OBJCOPY = auto()
    PACMAN = auto()
    PACMAN_KEY = auto()
    QEMU_IMG = auto()
    QEMU_NBD = auto()
    SBSIGN = auto()
    SFDISK = auto()
    SYNC = auto()
    SYSTEMCTL = auto()
    TAR = auto()
    USERADD = auto()
    USERMOD = auto()
    VERITYSETUP = auto()


def _check_for_binary(binary: str) -> str:
    """Check for binaries (with full path!)."""
    return binary if os.access(binary, os.X_OK) else ""


def _get_distribution():
    fallback = "<UNSUPPORTED>"
    with open("/usr/lib/os-release") as os_release:
        for line in os_release.readlines():
            line = line.strip()
            if line.startswith("ID_LIKE="):
                return line[8:].strip('"')
            if line.startswith("ID="):
                fallback = line[3:].strip('"')
    return fallback


def _find_binaries() -> typing.Dict[Binaries, str]:
    binaries = {
        Binaries.BORG: _check_for_binary("/usr/bin/borg"),
        Binaries.BTRFS: _check_for_binary("/usr/bin/btrfs"),
        Binaries.CHROOT_HELPER: _check_for_binary("/usr/bin/arch-chroot"),
        Binaries.DEPMOD: _check_for_binary("/usr/bin/depmod"),
        Binaries.FIND: _check_for_binary("/usr/bin/find"),
        Binaries.FLOCK: _check_for_binary("/usr/bin/flock"),
        Binaries.GROUPADD: _check_for_binary("/usr/sbin/groupadd"),
        Binaries.GROUPMOD: _check_for_binary("/usr/sbin/groupmod"),
        Binaries.MKFS_VFAT: _check_for_binary("/usr/bin/mkfs.vfat"),
        Binaries.MKNOD: _check_for_binary("/usr/bin/mknod"),
        Binaries.MKSQUASHFS: _check_for_binary("/usr/bin/mksquashfs"),
        Binaries.MODPROBE: _check_for_binary("/usr/bin/modprobe"),
        Binaries.NBD_CLIENT: _check_for_binary("/usr/bin/nbd-client"),
        Binaries.OBJCOPY: _check_for_binary("/usr/bin/objcopy"),
        Binaries.QEMU_IMG: _check_for_binary("/usr/bin/qemu-img"),
        Binaries.QEMU_NBD: _check_for_binary("/usr/bin/qemu-nbd"),
        Binaries.SBSIGN: _check_for_binary("/usr/bin/sbsign"),
        Binaries.SFDISK: _check_for_binary("/usr/bin/sfdisk"),
        Binaries.SYNC: _check_for_binary("/usr/bin/sync"),
        Binaries.SYSTEMCTL: _check_for_binary("/usr/bin/systemctl"),
        Binaries.TAR: _check_for_binary("/usr/bin/tar"),
        Binaries.USERADD: _check_for_binary("/usr/sbin/useradd"),
        Binaries.USERMOD: _check_for_binary("/usr/sbin/usermod"),
    }
    os_binaries: typing.Dict[Binaries, str] = {}
    distribution = _get_distribution()
    debug("Distribution: {}".format(distribution))
    if distribution == "debian":
        os_binaries = {
            Binaries.APT_GET: _check_for_binary("/usr/bin/apt-get"),
            Binaries.DEBOOTSTRAP: _check_for_binary("/usr/sbin/debootstrap"),
            Binaries.DPKG: _check_for_binary("/usr/bin/dpkg"),
            Binaries.VERITYSETUP: _check_for_binary("/usr/sbin/veritysetup"),
        }
    elif distribution == "arch" or distribution == "archlinux":
        os_binaries = {
            Binaries.PACMAN_KEY: _check_for_binary("/usr/bin/pacman-key"),
            Binaries.PACMAN: _check_for_binary("/usr/bin/pacman"),
            Binaries.VERITYSETUP: _check_for_binary("/usr/bin/veritysetup"),
        }
    else:
        fail('Unsupported Linux flavor (detected was "{}").'.format(distribution))

    return {**binaries, **os_binaries}


class BinaryManager:
    """The find and allow access to all the different system binaries
       Cleanroom may need."""

    def __init__(self) -> None:
        """Constructor."""
        self._binaries = _find_binaries()

    def preflight_check(self) -> None:
        passed = True
        for b in self._binaries.items():
            if b[1]:
                debug("{} found: {}...".format(b[0], b[1]))
            else:
                warn("{} not found.".format(b[0]))
                passed = False
        if not passed:
            raise PreflightError("Required binaries are not available.")

    def binary(self, selector: Binaries) -> str:
        """Get a binary from the context."""
        binary = self._binaries[selector]
        trace("Binary for {}: {}.".format(selector, binary))
        return binary
