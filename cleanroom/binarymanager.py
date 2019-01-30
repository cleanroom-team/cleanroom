# -*- coding: utf-8 -*-
"""An object used to find/get host system binaries.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .printer import debug, fail, trace, warn

from enum import Enum, auto, unique
import os
import typing


@unique
class Binaries(Enum):
    """Important binaries."""

    BORG = auto()
    BTRFS = auto()
    MKNOD = auto()
    PACMAN = auto()
    PACMAN_KEY = auto()
    PACSTRAP = auto()
    APT_GET = auto()
    DPKG = auto()
    DEBOOTSTRAP = auto()
    SBSIGN = auto()
    OBJCOPY = auto()
    MKSQUASHFS = auto()
    VERITYSETUP = auto()
    TAR = auto()
    USERMOD = auto()
    USERADD = auto()
    GROUPADD = auto()
    GROUPMOD = auto()
    CHROOT_HELPER = auto()


def _check_for_binary(binary: str) -> str:
    """Check for binaries (with full path!)."""
    return binary if os.access(binary, os.X_OK) else ''


def _get_distribution():
    with open("/usr/lib/os-release") as os_release:
        for line in os_release.readlines():
            line = line.strip()
            if line.startswith('ID_LIKE='):
                return line[8:].strip('"')
    return "<UNSUPPORTED>"


def _find_binaries() -> typing.Dict[Binaries, str]:
    binaries = {
        Binaries.BORG: _check_for_binary('/usr/bin/borg'),
        Binaries.BTRFS: _check_for_binary('/usr/bin/btrfs'),
        Binaries.SBSIGN: _check_for_binary('/usr/bin/sbsign'),
        Binaries.OBJCOPY: _check_for_binary('/usr/bin/objcopy'),
        Binaries.MKNOD: _check_for_binary('/usr/bin/mknod'),
        Binaries.MKSQUASHFS: _check_for_binary('/usr/bin/mksquashfs'),
        Binaries.TAR: _check_for_binary('/usr/bin/tar'),
        Binaries.USERMOD: _check_for_binary('/usr/sbin/usermod'),
        Binaries.USERADD: _check_for_binary('/usr/sbin/useradd'),
        Binaries.GROUPMOD: _check_for_binary('/usr/sbin/groupmod'),
        Binaries.GROUPADD: _check_for_binary('/usr/sbin/groupadd'),
        Binaries.CHROOT_HELPER: _check_for_binary('/usr/bin/arch-chroot'),
    }
    os_binaries: typing.Dict[Binaries, str] = {}
    distribution = _get_distribution()
    if distribution == "debian":
        os_binaries = {
            Binaries.APT_GET: _check_for_binary('/usr/bin/apt-get'),
            Binaries.DPKG: _check_for_binary('/usr/bin/dpkg'),
            Binaries.DEBOOTSTRAP: _check_for_binary('/usr/sbin/debootstrap'),
            Binaries.VERITYSETUP: _check_for_binary('/usr/sbin/veritysetup'),
        }
    elif distribution == "archlinux":
        os_binaries = {
            Binaries.PACMAN: _check_for_binary('/usr/bin/pacman'),
            Binaries.PACMAN_KEY: _check_for_binary('/usr/bin/pacman-key'),
            Binaries.PACSTRAP: _check_for_binary('/usr/bin/pacstrap'),
            Binaries.VERITYSETUP: _check_for_binary('/usr/bin/veritysetup'),
        }
    else:
        fail("Unsupported Linux flavor.")

    return {**binaries, **os_binaries}


class BinaryManager:
    """The find and allow access to all the different system binaries
       Cleanroom may need."""

    def __init__(self) -> None:
        """Constructor."""
        self._binaries = _find_binaries()

    def preflight_check(self) -> bool:
        passed = True
        for b in self._binaries.items():
            if b[1]:
                debug('{} found: {}...'.format(b[0], b[1]))
            else:
                warn('{} not found.'.format(b[0]))
                passed = False
        return passed

    def binary(self, selector: Binaries) -> typing.Optional[str]:
        """Get a binary from the context."""
        assert self._binaries

        binary = self._binaries[selector]
        trace('Binary for {}: {}.'.format(selector, binary))
        return binary
