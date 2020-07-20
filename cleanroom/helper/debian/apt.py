# -*- coding: utf-8 -*-
"""Manage apt and debootstrap calls.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from ...systemcontext import SystemContext
from ..run import run

import os
import os.path
import shutil
import stat
import typing


def _package_type(system_context: SystemContext) -> typing.Optional[str]:
    return system_context.substitution("CLRM_PACKAGE_TYPE", "")


def _apt_state(system_context: SystemContext) -> bool:
    return system_context.substitution("APT_INSTALL_STATE", str(False))


def _dpkg_state_directory(system_context: SystemContext, internal: bool = False) -> str:
    if internal:
        return system_context.file_name("/var/lib/dpkg")
    return os.path.join(system_context.meta_directory, "dpkg/state")


def _dpkg_config_directory(
    system_context: SystemContext, internal: bool = False
) -> str:
    if internal:
        return system_context.file_name("/etc/dpkg")
    return os.path.join(system_context.meta_directory, "dpkg/config")


def _apt_state_directory(system_context: SystemContext, internal: bool = False) -> str:
    if internal:
        return system_context.file_name("/var/lib/apt")
    return os.path.join(system_context.meta_directory, "apt/state")


def _apt_cache_directory(system_context: SystemContext, internal: bool = False) -> str:
    if internal:
        return system_context.file_name("/var/cache/apt")
    return os.path.join(system_context.cache_directory, "apt")


def _apt_config_directory(system_context: SystemContext, internal: bool = False) -> str:
    if internal:
        return system_context.file_name("/etc/apt")
    return os.path.join(system_context.meta_directory, "apt/config")


def _sanity_check(system_context: SystemContext) -> None:
    assert os.path.isdir(system_context.file_name("/var/lib/machines"))
    assert os.path.isdir(system_context.file_name("/var/lib/portables"))

    mode = os.stat(system_context.file_name("/dev/null")).st_mode
    assert stat.S_ISCHR(mode)


def debootstrap(
    system_context: SystemContext,
    *,
    suite: str,
    variant: str = "",
    target: str,
    mirror: str,
    include: typing.Optional[str] = None,
    exclude: typing.Optional[str] = None,
    debootstrap_command: str
) -> None:
    """Run debootstrap on host."""
    assert not _package_type(system_context)
    _sanity_check(system_context)

    assert suite
    assert target

    args: typing.List[str] = []
    if variant:
        args.append("--variant={}".format(variant))
    if include:
        args.append("--include={}".format(include))
    if exclude:
        args.append("--exclude={}".format(exclude))
    args += [suite, target]
    if mirror:
        args.append(mirror)

    # Debootstrap:
    run(debootstrap_command, *args)

    # De-dpkg-ize:
    root = system_context.fs_directory

    dpkg_state = _dpkg_state_directory(system_context, internal=False)
    apt_state = _apt_state_directory(system_context, internal=False)
    apt_cache = _apt_cache_directory(system_context, internal=False)
    apt_config = _apt_config_directory(system_context, internal=False)

    os.makedirs(os.path.join(system_context.meta_directory, "dpkg"))
    shutil.move(_dpkg_state_directory(system_context, internal=True), dpkg_state)
    shutil.move(
        _dpkg_config_directory(system_context, internal=True),
        _dpkg_config_directory(system_context, internal=False),
    )

    os.makedirs(os.path.join(system_context.meta_directory, "apt"))
    shutil.move(_apt_state_directory(system_context, internal=True), apt_state)
    shutil.move(_apt_cache_directory(system_context, internal=True), apt_cache)
    shutil.move(_apt_config_directory(system_context, internal=True), apt_config)

    os.makedirs(
        os.path.join(
            _apt_config_directory(system_context, internal=False), "preferences.d"
        )
    )

    # Copy over trust db if none exists yet:
    # FIXME: Create a new one?
    gpg_dir = os.path.join(
        _apt_config_directory(system_context, internal=False), "trusted.gpg.d"
    )
    if not os.path.isdir(gpg_dir):
        shutil.copytree("/etc/apt/trusted.gpg.d", gpg_dir)

    # Create apt configuration override:
    with open(
        os.path.join(system_context.meta_directory, "apt/config/override.conf"), "w"
    ) as apt_override:
        apt_override.write('Dir::Etc "{}";\n'.format(apt_config))
        apt_override.write(
            'DPkg::options {{"--admindir={}"; "--instdir={}";}};\n'.format(
                dpkg_state, root
            )
        )
        apt_override.write('Dir::State "{}";\n'.format(apt_state))
        apt_override.write('Dir::Cache "{}";\n'.format(apt_cache))
        apt_override.write('Dir::Log "{}";\n'.format(os.path.join(apt_cache, "log")))
        apt_override.write(
            'Dir::State::status "{}";\n'.format(os.path.join(dpkg_state, "status"))
        )


def apt(
    system_context: SystemContext,
    *packages: str,
    remove: bool = False,
    assume_installed: str = "",
    overwrite: str = ""
) -> None:
    """Use apt to install packages."""
    assert _package_type(system_context) == "deb"

    # FIXME: Implement this!


def apt_report(system_context: SystemContext, directory: str):
    """Print apt information into FS."""
    if _apt_state(system_context) == "True":
        return

    os.makedirs(directory)

    # FIXME: Implement this!
