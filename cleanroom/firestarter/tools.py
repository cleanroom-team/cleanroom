#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CleanRoom binary.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.printer import trace, verbose, debug
import cleanroom.helper.disk as disk
import cleanroom.helper.mount as mount

import os
from shutil import chown, copyfile
from distutils.dir_util import copy_tree
import subprocess
import sys
from tempfile import TemporaryDirectory
import typing


# Library:


def run(
    *args,
    work_directory: str = "",
    check: bool = True,
    env: typing.Dict[str, str] = os.environ
) -> subprocess.CompletedProcess:
    env["LC_ALL"] = "en_US.UTF-8"

    cwd = work_directory or None
    result = subprocess.run(args, env=env, capture_output=True, check=False, cwd=cwd)
    if result.returncode != 0:
        debug(
            "Borg returned with exit code {}:\nSTDOUT:\n{}\nSTDERR:\n{}.".format(
                result.returncode, result.stdout, result.stderr
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


def run_borg(*args, work_directory: str = "") -> subprocess.CompletedProcess:
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


def extract_archive(archive: str, target_directory: str, *, repository: str) -> None:
    run_borg(
        "extract", "{}::{}".format(repository, archive), work_directory=target_directory
    )


def write_image(
    system_name: str, target_directory: str, *, repository: str, version: str = ""
) -> str:
    (archive_to_extract, extracted_version) = find_archive(
        system_name, repository=repository, version=version
    )
    if not archive_to_extract:
        if version:
            print(
                'Could not find version "{}" of system "{}" to extract.'.format(
                    version, system_name
                )
            )
        else:
            print('Could not find system "{}" to extract'.format(system_name))
        sys.exit(2)

    extract_archive(archive_to_extract, target_directory, repository=repository)

    return extracted_version


def export_into_directory(
    system_name: str,
    target_directory: str,
    *,
    repository: str,
    version: str = "",
    create_directory: bool = False,
    owner: str = "",
    group: str = "",
    mode: int = 0
) -> str:
    if not os.path.isdir(target_directory):
        if create_directory:
            os.makedirs(target_directory)

    assert os.path.isdir(target_directory)

    with TemporaryDirectory(prefix="clrm_dir_", dir=target_directory) as tempdir:
        extracted_version = write_image(
            system_name, tempdir, repository=repository, version=version
        )

        exported_file_name = "clrm_{}".format(extracted_version)
        exported_file = os.path.join(tempdir, exported_file_name)
        assert os.path.isfile(exported_file)

        if group or owner:
            chown(exported_file, user=owner or "root", group=group or "root")
        if mode:
            os.chmod(exported_file, mode)

        target_file = os.path.join(target_directory, exported_file_name)
        os.rename(exported_file, target_file)

        # Create symlink:
        link_location = os.path.join(target_directory, "latest.img")
        if os.path.islink(link_location):
            os.unlink(link_location)
        os.symlink("./{}".format(exported_file_name), link_location)
        if group or owner:
            chown(link_location, user=owner or "root", group=group or "root")

        return target_file


def copy_efi_partition(
    *, image_file: str, efi_device, tempdir: str, kernel_only: bool = True
):
    verbose("Copying EFI configuration out of image file.")
    with disk.NbdDevice(image_file, disk_format="raw") as internal_device:
        internal_device.wait_for_device_node(partition=1)
        with mount.Mount(
            internal_device.device(1), os.path.join(tempdir, "_efi")
        ) as int_efi:
            with mount.Mount(
                efi_device, os.path.join(tempdir, "efi"), fs_type="vfat"
            ) as efi:
                if kernel_only:
                    img_dir = os.path.join(int_efi, "EFI", "Linux")
                    efi_dir = os.path.join(efi, "EFI", "Linux")
                    assert os.path.isdir(img_dir)
                    if not os.path.isdir(efi_dir):
                        os.makedirs(efi_dir)

                    for f in [
                        f
                        for f in os.listdir(img_dir)
                        if os.path.isfile(os.path.join(img_dir, f))
                    ]:
                        trace("Copying EFI kernel {}.".format(f))
                        copyfile(os.path.join(img_dir, f), os.path.join(efi_dir, f))
                else:
                    trace("Copying EFI folder into system.")
                    copy_tree(int_efi, efi)


def execute_with_system_mounted(
    to_execute: typing.Callable[[str, str], None],
    *,
    repository: str,
    system_name: str,
    system_version: str = ""
) -> None:
    with TemporaryDirectory(prefix="clrm_qemu_") as tempdir:
        verbose("Extracting image")
        image_path = export_into_directory(
            system_name, tempdir, repository=repository, version=system_version
        )

        assert os.path.isfile(image_path)

        with disk.NbdDevice(image_path, disk_format="raw") as device:
            verbose("Mounting EFI...")
            device.wait_for_device_node(partition=1)
            with mount.Mount(
                device.device(1),
                os.path.join(tempdir, "EFI"),
                fs_type="vfat",
                options="ro",
            ) as efi:
                verbose("Mounting root filesystem...")
                with mount.Mount(
                    device.device(2),
                    os.path.join(tempdir, "root"),
                    fs_type="squashfs",
                    options="ro",
                ) as root:

                    verbose('Executing with EFI "{}" and root "{}".'.format(efi, root))
                    to_execute(efi, root)
