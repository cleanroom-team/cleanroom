# -*- coding: utf-8 -*-
"""Manage the dnf packager.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.printer import debug, info
from cleanroom.systemcontext import SystemContext
from cleanroom.helper.run import run
from cleanroom.helper.mount import umount_all, mount

import os
import os.path
import shutil
import typing


def _package_type(system_context: SystemContext) -> typing.Optional[str]:
    return system_context.substitution("CLRM_PACKAGE_TYPE", "")


def _set_package_type(system_context: SystemContext):
    system_context.set_substitution("CLRM_PACKAGE_TYPE", "fedora")


def _has_dnf_installed(system_context: SystemContext) -> bool:
    return os.path.isfile(system_context.file_name("/usr/bin/dnf"))


def _has_rpm_installed(system_context: SystemContext) -> bool:
    return os.path.isfile(system_context.file_name("/usr/bin/rpm"))


def _outside_config_file_location(system_context: SystemContext) -> str:
    return os.path.join(system_context.cache_directory, "dnf.conf")


def _rpm_dir(system_context: SystemContext) -> str:
    return os.path.join(system_context.fs_directory, "usr/lib/sysimage/rpm")


def _outside_rpm_dir(system_context: SystemContext) -> str:
    return os.path.join(system_context.cache_directory, "sysimage/rpm")


def _dnf_dir(system_context: SystemContext) -> str:
    return os.path.join(system_context.fs_directory, "usr/lib/sysimage/dnf")


def _outside_dnf_dir(system_context: SystemContext) -> str:
    return os.path.join(system_context.cache_directory, "sysimage/dnf")


def _mount(src: str, dest: str, **kwargs):
    if not os.path.isdir(src):
        os.makedirs(src)
    if not os.path.isdir(dest):
        os.makedirs(dest)

    mount(src, dest, **kwargs)


def _setup_dnf(system_context: SystemContext):
    info("Setting up dnf directories.")
    rpm_dir = _rpm_dir(system_context)
    if not os.path.isdir(rpm_dir):
        os.makedirs(rpm_dir)
        var_rpm_dir = os.path.join(system_context.fs_directory, "var/lib")
        if not os.path.isdir(var_rpm_dir):
            os.makedirs(var_rpm_dir)
        os.symlink(
            "../../usr/lib/sysimage/rpm",
            os.path.join(var_rpm_dir, "rpm"),
            target_is_directory=True,
        )
        debug("RPM directory created in /usr/lib/sysimage.")

    if not _has_rpm_installed(system_context):
        _mount(
            _outside_rpm_dir(system_context), _rpm_dir(system_context), options="bind"
        )

    if not _has_dnf_installed(system_context):
        _mount(
            _outside_dnf_dir(system_context), _dnf_dir(system_context), options="bind"
        )

    debug("Set up for DNF run...")


def _teardown_dnf(system_context: SystemContext):
    umount_all("/usr/lib/sysimage/rpm", system_context.fs_directory)
    umount_all("/usr/lib/sysimage/dnf", system_context.fs_directory)


def _dnf_args(
    system_context: SystemContext,
) -> typing.List[str]:
    return [
        f"--config={_outside_config_file_location(system_context)}",
        f"--installroot={system_context.fs_directory}",
        "--releasever=/",
        "--assumeyes",
        "--noplugins",
    ]


def _run_dnf(
    system_context: SystemContext,
    *args: str,
    dnf_command: str,
    **kwargs: typing.Any,
) -> None:
    _setup_dnf(system_context)

    all_args = _dnf_args(system_context) + list(args)
    run(
        dnf_command,
        *all_args,
        work_directory=system_context.systems_definition_directory,
        timeout=600,
        **kwargs,
    )

    _teardown_dnf(system_context)


def _move_dirs(
    name: str, system_name: str, inside_dir: str, outside_dir: str, move_into: bool
):
    direction = "into" if move_into else "out of"
    debug(f'Moving {name} data {direction} system "{system_name}".')

    src, dest = inside_dir, outside_dir

    if move_into:
        src, dest = dest, src

    os.removedirs(dest)
    shutil.copytree(src, dest)
    shutil.rmtree(src)


def _move_rpm_data(system_context: SystemContext, *, move_into_fs: bool):
    _move_dirs(
        "RPM",
        system_context.system_name,
        _rpm_dir(system_context),
        _outside_rpm_dir(system_context),
        move_into_fs,
    )


def _move_dnf_data(system_context: SystemContext, *, move_into_fs: bool):
    target_path = os.path.join(system_context.fs_directory, "etc/dnf/dnf.conf")
    if os.path.isfile(target_path):
        os.remove(target_path)

    assert os.path.isfile(_outside_config_file_location(system_context))
    shutil.copyfile(_outside_config_file_location(system_context), target_path)

    _move_dirs(
        "DNF",
        system_context.system_name,
        _dnf_dir(system_context),
        _outside_dnf_dir(system_context),
        move_into_fs,
    )


def dnf(
    system_context: SystemContext,
    *packages: str,
    remove: bool = False,
    group_levels: typing.Sequence[str] = [],
    exclude: typing.Sequence[str] = [],
    dnf_command: str,
    config: str = "",
) -> None:
    """Use dnf to install packages."""
    previous_dnfstate = _has_dnf_installed(system_context)
    previous_rpmstate = _has_rpm_installed(system_context)

    if not _package_type(system_context):
        _set_package_type(system_context)

    assert _package_type(system_context) == "fedora"

    if config:
        debug(f"Moving config file {config} into place...")
        outside_dnf_config = _outside_config_file_location(system_context)
        assert not os.path.isfile(outside_dnf_config)
        shutil.copyfile(config, outside_dnf_config)

    assert os.path.isfile(_outside_config_file_location(system_context))

    action: typing.List[str] = []

    if remove:
        info("Removing {}".format(", ".join(packages)))
        action = ["remove"]
    else:
        info("Installing {}".format(", ".join(packages)))
        action = ["install"]

    if group_levels:
        levels_string = ",".join(group_levels)
        debug(f"Group levels given as: {group_levels} => {levels_string}.")
        action.append(f"--setopt=group_package_types={levels_string}")

    if exclude:
        exclude_string = ",".join(exclude)
        debug(f"Exclude given as {exclude} => {exclude_string}.")
        action.append(f"--exclude={exclude_string}")

    debug(f"DNF Action to do: {action}.")

    _run_dnf(
        system_context,
        *action,
        *packages,
        dnf_command=dnf_command,
    )

    assert os.path.isfile(_outside_config_file_location(system_context))

    rpmstate = _has_rpm_installed(system_context)
    if previous_rpmstate != rpmstate:
        _move_rpm_data(system_context, move_into_fs=rpmstate)
    assert os.path.isfile(_outside_config_file_location(system_context))

    dnfstate = _has_dnf_installed(system_context)
    if previous_dnfstate != dnfstate:
        _move_dnf_data(system_context, move_into_fs=dnfstate)
    assert os.path.isfile(_outside_config_file_location(system_context))
