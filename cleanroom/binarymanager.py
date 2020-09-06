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
    LSOF = auto()
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


def _check_for_abs_binary(binary: str) -> str:
    assert os.path.isabs(binary)
    return binary if os.access(binary, os.X_OK) else ""


def _check_for_one_binary(binary: str) -> str:
    if os.path.isabs(binary):
        return _check_for_abs_binary(binary)

    for d in ["/usr/bin", "/usr/sbin", "/bin", "/sbin"]:
        result = os.path.join(d, binary)
        if result:
            return result

    return ""


def _check_for_binary(*binaries: str) -> str:
    """Check for binaries."""
    for b in binaries:
        result = _check_for_one_binary(b)
        if result:
            return result

    return ""


def _find_binaries() -> typing.Dict[Binaries, str]:
    return {
        Binaries.APT_GET: _check_for_binary("apt-get"),
        Binaries.BORG: _check_for_binary("borg"),
        Binaries.BTRFS: _check_for_binary("btrfs"),
        Binaries.CHROOT_HELPER: _check_for_binary("arch-chroot"),
        Binaries.DEPMOD: _check_for_binary("depmod"),
        Binaries.DPKG: _check_for_binary("dpkg"),
        Binaries.FIND: _check_for_binary("find"),
        Binaries.FLOCK: _check_for_binary("flock"),
        Binaries.GROUPADD: _check_for_binary("groupadd"),
        Binaries.GROUPMOD: _check_for_binary("groupmod"),
        Binaries.LSOF: _check_for_binary("lsof"),
        Binaries.MKFS_VFAT: _check_for_binary("mkfs.vfat"),
        Binaries.MKNOD: _check_for_binary("mknod"),
        Binaries.MKSQUASHFS: _check_for_binary("mksquashfs"),
        Binaries.MODPROBE: _check_for_binary("modprobe"),
        Binaries.NBD_CLIENT: _check_for_binary("nbd-client"),
        Binaries.OBJCOPY: _check_for_binary("objcopy"),
        Binaries.QEMU_IMG: _check_for_binary("qemu-img"),
        Binaries.QEMU_NBD: _check_for_binary("qemu-nbd"),
        Binaries.SBSIGN: _check_for_binary("sbsign"),
        Binaries.SFDISK: _check_for_binary("sfdisk"),
        Binaries.SYNC: _check_for_binary("sync"),
        Binaries.SYSTEMCTL: _check_for_binary("systemctl"),
        Binaries.TAR: _check_for_binary("tar"),
        Binaries.USERADD: _check_for_binary("useradd"),
        Binaries.USERMOD: _check_for_binary("usermod"),
        Binaries.DEBOOTSTRAP: _check_for_binary("debootstrap"),
        Binaries.VERITYSETUP: _check_for_binary("veritysetup"),
        Binaries.PACMAN_KEY: _check_for_binary("pacman-key"),
        Binaries.PACMAN: _check_for_binary("pacman"),
        Binaries.VERITYSETUP: _check_for_binary("veritysetup"),
    }


class BinaryManager:
    """The find and allow access to all the different system binaries
       Cleanroom may need."""

    def __init__(self) -> None:
        """Constructor."""
        self._binaries = _find_binaries()
        self._optionals = set(
            [
                Binaries.APT_GET,
                Binaries.DEBOOTSTRAP,
                Binaries.DPKG,
                Binaries.PACMAN,
                Binaries.PACMAN_KEY,
            ]
        )

    def preflight_check(self) -> None:
        passed = True
        for b in self._binaries.items():
            if b[1]:
                debug("{} found: {}...".format(b[0], b[1]))
            else:
                if b in self._optionals:
                    debug("{} not found [OPTIONAL].")
                else:
                    warn("{} not found.".format(b[0]))
                    passed = False
        if not passed:
            raise PreflightError("Required binaries are not available.")

    def binary(self, selector: Binaries) -> str:
        """Get a binary from the context."""
        return self._binaries[selector]
