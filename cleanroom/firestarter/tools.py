#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CleanRoom binary.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.printer import trace, verbose, debug
import cleanroom.helper.disk as disk
import cleanroom.helper.mount as mount

import os
import subprocess
import typing


# Library:


def run(
    *args: str,
    work_directory: str = "",
    check: bool = True,
    env: typing.Any = os.environ,  ## What is a better type for this?
) -> subprocess.CompletedProcess:
    env["LC_ALL"] = "en_US.UTF-8"

    cwd = work_directory or None
    trace('Running: "{}"...'.format('" "'.join(args)))
    result = subprocess.run(args, env=env, capture_output=True, check=False, cwd=cwd)
    if result.returncode != 0:
        debug(
            "Command returned with exit code {}:\nSTDOUT:\n{}\nSTDERR:\n{}.".format(
                result.returncode,
                result.stdout.decode("utf-8"),
                result.stderr.decode("utf-8"),
            )
        )
    if result.returncode == 2 and check:
        raise subprocess.CalledProcessError(
            returncode=result.returncode,
            cmd=args,
            output=result.stdout,
            stderr=result.stderr,
        )

    return result


def run_borg(*args: str, work_directory: str = "") -> subprocess.CompletedProcess:
    return run("/usr/bin/borg", *args, work_directory=work_directory)


def find_archive(
    system_name: str, *, repository: str, version: str = ""
) -> typing.Tuple[str, str]:
    borg_list = run_borg("list", repository)

    archive_to_use = ""
    for line in borg_list.stdout.decode("utf-8").split("\n"):
        if not line.startswith(system_name):
            continue
        trace("Borg list: {}.".format(line))
        versioned_system_name = line.split(" ")[0]
        assert versioned_system_name[len(system_name)] == "-"
        current_version = versioned_system_name[len(system_name) + 1 :]
        if version:
            if current_version == version:
                archive_to_use = versioned_system_name
                break
        else:
            if not archive_to_use or versioned_system_name > archive_to_use:
                archive_to_use = versioned_system_name

    return archive_to_use, archive_to_use[len(system_name) + 1 :]


def execute_with_system_mounted(
    to_execute: typing.Callable[[str, str], int], *, image_file: str, tmp_dir: str
) -> int:
    assert os.path.isfile(image_file)

    with disk.NbdDevice(image_file, disk_format="raw", read_only=True) as device:
        verbose("Mounting EFI...")
        device.wait_for_device_node(partition=1)
        with mount.Mount(
            device.device(1),
            os.path.join(tmp_dir, "EFI"),
            fs_type="vfat",
            options="ro",
        ) as efi:
            verbose("Mounting root filesystem...")
            with mount.Mount(
                device.device(2),
                os.path.join(tmp_dir, "root"),
                fs_type="squashfs",
                options="ro",
            ) as root:

                trace('Executing with EFI "{}" and root "{}".'.format(efi, root))
                result = to_execute(efi, root)

    return result


class BorgMount:
    def __init__(
        self, mnt_point: str, *, repository: str, system_name: str, version: str,
    ) -> None:
        if not os.path.isdir(mnt_point):
            raise OSError('Mount point "{}" is not a directory.'.format(mnt_point))

        (archive, _) = find_archive(system_name, repository=repository, version=version)
        if not archive:
            raise OSError("Failed to find repository or system.")

        self._mnt_point = mnt_point
        self._repository = repository
        self._archive = archive
        self._version = version

    def __enter__(self) -> typing.Any:
        run_borg(
            "mount", "{}::{}".format(self._repository, self._archive), self._mnt_point
        )

        # find image file:
        image_files = [
            f
            for f in os.listdir(self._mnt_point)
            if self._version in f and os.path.isfile(os.path.join(self._mnt_point, f))
        ]
        assert len(image_files) == 1

        return os.path.join(self._mnt_point, image_files[0])

    def __exit__(
        self, exc_type: typing.Any, exc_val: typing.Any, exc_tb: typing.Any
    ) -> None:
        mount.umount(self._mnt_point)
