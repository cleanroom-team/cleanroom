# -*- coding: utf-8 -*-
"""Manage pacman and pacstrap calls.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from ...printer import debug, info
from ...systemcontext import SystemContext
from ..run import run
from ..mount import umount_all, mount

import os
import os.path
import shutil
import stat
import typing


def _package_type(system_context: SystemContext) -> typing.Optional[str]:
    return system_context.substitution("CLRM_PACKAGE_TYPE", "")


def _set_package_type(system_context: SystemContext) -> None:
    system_context.set_substitution("CLRM_PACKAGE_TYPE", "pacman")


def _fs_directory(system_context: SystemContext) -> str:
    return system_context.fs_directory


def _pacman_directory(system_context: SystemContext, internal: bool = False) -> str:
    return (
        system_context.file_name("/usr/lib/pacman")
        if internal
        else os.path.join(system_context.meta_directory, "pacman")
    )


def _config_file(system_context: SystemContext, internal: bool = False) -> str:
    return (
        system_context.file_name("/etc/pacman.conf")
        if internal
        else os.path.join(_pacman_directory(system_context, internal), "pacman.conf")
    )


def _db_directory(system_context: SystemContext, internal: bool = False) -> str:
    return os.path.join(_pacman_directory(system_context, internal), "db")


def _hooks_directory(system_context: SystemContext, internal: bool = False) -> str:
    return os.path.join(_pacman_directory(system_context, internal), "hooks")


def gpg_directory(system_context: SystemContext, internal: bool = False) -> str:
    """Return the host location of the pacman GPG configuration."""
    return os.path.join(_pacman_directory(system_context, internal), "gpg")


def _base_cache_directory(system_context: SystemContext, internal: bool = False) -> str:
    return (
        os.path.join(system_context.fs_directory, "var/cache")
        if internal
        else system_context.cache_directory
    )


def _cache_directory(system_context: SystemContext, internal: bool = False) -> str:
    """Return the host location of the pacman GPG configuration."""
    return os.path.join(_base_cache_directory(system_context, internal), "pacman")


def _log(system_context: SystemContext, internal: bool = False) -> str:
    return os.path.join(_cache_directory(system_context, internal), "log")


def _setup_directories(system_context: SystemContext, internal: bool) -> None:
    info("Setting up pacman directories.")
    if not os.path.isdir(_pacman_directory(system_context, internal)):
        os.makedirs(_pacman_directory(system_context, internal))
        debug("Main pacman directory created.")
    os.makedirs(_db_directory(system_context, internal))
    debug("DB directory created.")
    os.makedirs(
        os.path.join(gpg_directory(system_context, internal), "private-keys-v1.d")
    )
    debug("GPG directory created.")
    os.makedirs(_hooks_directory(system_context, internal))
    debug("Hook directory created.")

    cache = _cache_directory(system_context, internal)
    if not os.path.isdir(cache):
        os.makedirs(cache)
    debug("Cache directory created.")


def _sanity_check(system_context: SystemContext) -> None:
    assert os.path.isdir(system_context.file_name("/var/lib/machines"))
    assert os.path.isdir(system_context.file_name("/var/lib/portables"))

    mode = os.stat(system_context.file_name("/dev/null")).st_mode
    assert stat.S_ISCHR(mode)


def _pacman_args(
    system_context: SystemContext, installed_pacman: bool = False
) -> typing.List[str]:
    return [
        "--config",
        _config_file(system_context, internal=installed_pacman),
        "--root",
        _fs_directory(system_context),
        "--cachedir",
        _cache_directory(system_context, internal=installed_pacman),
        "--dbpath",
        _db_directory(system_context, internal=installed_pacman),
        "--hookdir",
        _hooks_directory(system_context, internal=installed_pacman),
        "--logfile",
        _log(system_context, internal=installed_pacman),
        "--gpgdir",
        gpg_directory(system_context, internal=installed_pacman),
        "--noconfirm",
    ]


def _pacman_keyinit(system_context: SystemContext, pacman_key_command: str) -> None:
    run(
        pacman_key_command,
        "--init",
        "--gpgdir",
        gpg_directory(system_context),
        work_directory=system_context.systems_definition_directory,
    )


def _mountpoint(root_dir: str, folder: str, dev: str, **kwargs: typing.Any):
    debug("Mounting {} in chroot.".format(folder))
    path = root_dir
    if folder:
        path = os.path.join(root_dir, folder)

    if not os.path.isdir(path):
        os.makedirs(path)
    mount(dev, path, **kwargs)


def _mount_directories_if_needed(root_dir: str, *, pacman_in_filesystem: bool = False):
    debug("Preparing pacman chroot for external pacman run.")
    _mountpoint(root_dir, "", root_dir, options="bind")
    _mountpoint(root_dir, "proc", "proc", options="nosuid,noexec,nodev", fs_type="proc")
    _mountpoint(root_dir, "dev", "udev", options="mode=0755,nosuid", fs_type="devtmpfs")
    _mountpoint(root_dir, "sys", "/sys", options="bind,ro")
    _mountpoint(root_dir, "run", "/run", options="bind")
    _mountpoint(
        root_dir,
        "tmp",
        "tmp",
        options="mode=1777,strictatime,nodev,nosuid",
        fs_type="tmpfs",
    )


def _kill_processes_in(root_dir: str):
    result = run("/usr/bin/lsof")
    result.check_returncode()

    pids: typing.List[str] = []
    for line in result.stdout.split("\n"):
        if f" {root_dir}/" in line:
            pid = line.split(None, 2)[1]
            pids.append(pid)

    if pids:
        pids = list(set(pids))
        result = run("/usr/bin/kill", "-9", *pids)
        result.check_returncode()


def _umount_directories_if_needed(root_dir: str, *, pacman_in_filesystem: bool = False):
    debug("Cleaning up pacman chroot.")
    umount_all(root_dir)


def _run_pacman(
    system_context: SystemContext,
    *args: str,
    pacman_command: str,
    pacman_in_filesystem: bool,
    **kwargs: typing.Any,
) -> None:
    _sanity_check(system_context)

    all_args = _pacman_args(system_context, pacman_in_filesystem) + list(args)
    run(
        pacman_command,
        *all_args,
        work_directory=system_context.systems_definition_directory,
        timeout=600,
        **kwargs,
    )


def pacman_setup(system_context: SystemContext, config: str) -> None:
    assert not _package_type(system_context)
    _set_package_type(system_context)

    info("Setting up directories for pacman.")
    _setup_directories(system_context, False)
    shutil.copyfile(config, _config_file(system_context, False))


def pacman_keyinit(system_context: SystemContext, pacman_key_command: str) -> None:
    assert _package_type(system_context) == "pacman"

    info("Setting up pacman's keyring.")
    _pacman_keyinit(system_context, pacman_key_command)


def pacstrap(
    system_context: SystemContext,
    *packages: str,
    config: str,
    pacman_command: str,
    chroot_helper: str,
) -> None:
    """Run pacstrap on host."""
    assert _package_type(system_context) == "pacman"

    # Make sure pacman DB is up-to-date:
    _run_pacman(
        system_context, "-Sy", pacman_command=pacman_command, pacman_in_filesystem=False
    )
    _run_pacman(
        system_context, "-Fy", pacman_command=pacman_command, pacman_in_filesystem=False
    )

    pacman(
        system_context,
        *packages,
        pacman_command=pacman_command,
        chroot_helper=chroot_helper,
    )


def _copy_state(system_context: SystemContext, internal_pacman: bool) -> None:
    outside = _db_directory(system_context, False)
    inside = _db_directory(system_context, True)
    debug("Copying configuration file.")
    shutil.copyfile(
        _config_file(system_context, not internal_pacman),
        _config_file(system_context, internal_pacman),
    )

    debug("Inside: {}, outside: {}".format(inside, outside))
    if internal_pacman:
        shutil.rmtree(inside)
        info("Copy pacman DB into the filesystem.")
        shutil.copytree(outside, inside)
        info("Copy pacman GPG data into the filesystem.")
        shutil.rmtree(gpg_directory(system_context, True))
        shutil.copytree(
            gpg_directory(system_context, False), gpg_directory(system_context, True)
        )
        debug("Removing pacman DB outside the filesystem.")
        shutil.rmtree(outside)
    else:
        debug("Copy pacman DB out of the filesystem.")
        shutil.copytree(inside, outside)
        debug("Removing pacman DB inside the filesystem.")
        shutil.rmtree(inside)


def _move_pacman_data(system_context: SystemContext, *, move_into_fs: bool) -> None:
    debug('Moving pacman data for system "{}".'.format(system_context.system_name))

    _setup_directories(system_context, move_into_fs)

    info("Copying pacman state.")
    _copy_state(system_context, move_into_fs)


def pacman(
    system_context: SystemContext,
    *packages: str,
    remove: bool = False,
    assume_installed: str = "",
    overwrite: str = "",
    pacman_command: str,
    chroot_helper: str,
) -> None:
    """Use pacman to install packages."""
    previous_pacstate = os.path.isfile(system_context.file_name("/usr/bin/pacman"))

    assert _package_type(system_context) == "pacman"

    if remove:
        info("Removing {}".format(", ".join(packages)))
        action = ["-Rs"]
    else:
        info("Installing {}".format(", ".join(packages)))
        action = ["-S", "--needed"]
        if overwrite:
            action += ["--overwrite", overwrite]
        if assume_installed:
            action += ["--assume-installed", assume_installed]

    _mount_directories_if_needed(
        system_context.fs_directory, pacman_in_filesystem=previous_pacstate
    )
    _run_pacman(
        system_context,
        *action,
        *packages,
        pacman_command=pacman_command,
        pacman_in_filesystem=previous_pacstate,
    )

    # Kill processes that pacman might have started (incl. gpg-agents)
    _kill_processes_in(system_context.scratch_directory)

    _umount_directories_if_needed(
        system_context.fs_directory, pacman_in_filesystem=previous_pacstate
    )

    var_lib_pacman = system_context.file_name("/var/lib/pacman")
    if os.path.isdir(var_lib_pacman):
        shutil.rmtree(var_lib_pacman)

    pacstate = os.path.isfile(system_context.file_name("/usr/bin/pacman"))
    if previous_pacstate != pacstate:
        if pacstate:
            info(
                "Pacman got installed, "
                'moving pacman data into system "{}".'.format(
                    system_context.system_name
                )
            )
        else:
            info(
                "Pacman got deinstalled, "
                'moving pacman data out of system "{}".'.format(
                    system_context.system_name
                )
            )

        _move_pacman_data(system_context, move_into_fs=pacstate)

        # Update DB:
        if pacstate:
            info("Upgrading pacman DB.")
            run(
                "/usr/bin/pacman-db-upgrade",
                chroot_helper=chroot_helper,
                chroot=system_context.fs_directory,
            )


def pacman_report(
    system_context: SystemContext, directory: str, *, pacman_command: str
) -> None:
    """Print pacman information into FS."""
    if os.path.isfile(system_context.file_name("/usr/bin/pacman")):
        return

    os.makedirs(directory)

    qi = os.path.join(directory, "pacman-Qi.txt")
    action = ["-Qi"]
    _run_pacman(
        system_context,
        *action,
        stdout=qi,
        pacman_command=pacman_command,
        pacman_in_filesystem=False,
    )

    # Generate file list:
    ql_in = os.path.join(directory, "pacman-Ql.txt.in")
    action = ["-Ql"]
    _run_pacman(
        system_context,
        *action,
        stdout=ql_in,
        pacman_command=pacman_command,
        pacman_in_filesystem=False,
    )

    # Filter prefix from file list:
    with open(ql_in, "r") as input_fd:
        with open(os.path.join(directory, "pacman-Ql.txt"), "w") as output_fd:
            for line in input_fd:
                output_fd.write(line.replace(system_context.fs_directory, ""))

    # Remove prefix-ed version:
    os.remove(ql_in)
