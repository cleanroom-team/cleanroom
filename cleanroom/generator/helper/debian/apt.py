# -*- coding: utf-8 -*-
"""Manage apt and debootstrap calls.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from ...context import Binaries
from ...systemcontext import SystemContext
from ....exceptions import GenerateError
from ....printer import debug, info, verbose

import os
import os.path
import shutil
import stat
import typing


def _package_type(system_context: SystemContext) -> typing.Optional[str]:
    return system_context.substitution('CLRM_PACKAGE_TYPE', '')


def _set_package_type(system_context: SystemContext) -> None:
    system_context.set_substitution('CLRM_PACKAGE_TYPE', 'deb')


def _apt_state(system_context: SystemContext) -> bool:
    return system_context.substitution('APT_INSTALL_STATE', str(False))


def _set_apt_state(system_context: SystemContext, internal: bool=False) -> None:
    system_context.set_substitution('APT_INSTALL_STATE', str(internal))


def _fs_directory(system_context: SystemContext) -> str:
    return system_context.fs_directory()


def _dpkg_state_directory(system_context: SystemContext, internal: bool=False) -> str:
    if internal:
        return system_context.file_name('/usr/lib/dpkg/state')
    return os.path.join(system_context.meta_directory(), 'dpkg-state')

def _apt_state_directory(system_context: SystemContext, internal: bool=False) -> str:
    if internal:
        return system_context.file_name('/usr/lib/apt/state')
    return os.path.join(system_context.meta_directory(), 'apt-state')

def _dpkg_admin_directory(system_context: SystemContext, internal: bool=False) -> str:
    if internal:
        return system_context.file_name('/etc/dpkg')
    return os.path.join(system_context.meta_directory(), 'dpkg')

def _apt_admin_directory(system_context: SystemContext, internal: bool=False) -> str:
    if internal:
        return system_context.file_name('/etc/apt')
    return os.path.join(system_context.meta_directory(), 'apt')


def _sanity_check(system_context: SystemContext) -> None:
    assert os.path.isdir(system_context.file_name('/var/lib/machines'))
    assert os.path.isdir(system_context.file_name('/var/lib/portables'))

    mode = os.stat(system_context.file_name('/dev/null')).st_mode
    assert stat.S_ISCHR(mode)


def debootstrap(system_context: SystemContext, *, suite: str, target: str,
                mirror: str) -> None:
    """Run debootstrap on host."""
    assert not _package_type(system_context)
    _sanity_check(system_context)

    assert suite
    assert target

    args = [suite, target,]
    if mirror:
        args += [mirror,]

    system_context.run(system_context.binary(Binaries.DEBOOTSTRAP),
                       *args, outside=True)


def apt(system_context: SystemContext, *packages: str,
        remove: bool=False, assume_installed: str='', overwrite: str='') -> None:
    """Use apt to install packages."""
    assert _package_type(system_context) == 'deb'

    ## FIXME: Implement this!


def apt_report(system_context: SystemContext, directory: str):
    """Print apt information into FS."""
    if _apt_state(system_context) == 'True':
        return

    os.makedirs(directory)

    ## FIXME: Implement this!

