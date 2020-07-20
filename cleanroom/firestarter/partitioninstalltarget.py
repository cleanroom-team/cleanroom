#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Partitioning install target

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.printer import error, trace
import cleanroom.helper.disk as disk
import cleanroom.helper.run as run

from cleanroom.firestarter.installtarget import InstallTarget

import os
import typing


def validate_device(dev: str, dir: str) -> typing.Tuple[str, str, str]:
    if not os.path.isdir(dir):
        ("{} is not a directory.".format(dir))
        return ("", "", "")

    if not disk.is_block_device(dev):
        ("{} is not a block device.".format(dev))
        return ("", "", "")

    return (dev, "raw", dir)


def validate_image(
    file: str, format: str, size: str, dir: str
) -> typing.Tuple[str, str, str]:
    if not os.path.isdir(dir):
        ("{} is not a directory.".format(dir))
        return ("", "", "")

    if file.startswith("/dev/") or file.startswith("/sys/"):
        ('"{}" does not look like a image file name.'.format(file))
        return ("", "", "")
    if not os.path.exists(file):
        if not size:
            ('No size for missing image file "{}"'.format(file))
            return ("", "", "")
        disk.create_image_file(file, disk.byte_size(size), disk_format=format)

    if not os.path.isfile(file):
        ('"{}" exists but is no file.'.format(file))
        return ("", "", "")

    return (file, format, dir)


def parse_arguments(args: typing.Any) -> typing.List[typing.Tuple[str, str, str]]:
    device_list: typing.List[typing.Tuple[str, str, str]] = []
    device_map: typing.Dict[str, bool] = {}

    for m in args.mappings:
        parts = m.split(":")
        (dev, format, dir) = ("", "", "")
        trace("==> {}.".format(":".join(parts)))

        if len(parts) == 2:
            (dev, format, dir) = validate_device(*parts)
        elif len(parts) == 3:
            (dev, format, dir) = validate_image(parts[0], parts[1], "", parts[2])
        elif len(parts) == 4:
            (dev, format, dir) = validate_image(parts[0], parts[1], parts[2], parts[3])

        if not dev or not dir:
            error('Failed to parse device mapping "{}"'.format(m))
            return []

        if dev in device_map:
            error('Multiple definitions of device "{}".'.format(dev))
            return []
        else:
            device_map[dev] = True

        device_list.append((dev, format, dir))

    return device_list


def create_device(dev: str, format: str) -> disk.Device:
    if os.path.isfile(dev):
        return disk.NbdDevice(dev, disk_format=format)
    assert format == "raw"
    return disk.Device(dev)


class PartitionInstallTarget(InstallTarget):
    def __init__(self) -> None:
        super().__init__("partition", "Partition installation devices")

    def setup_subparser(self, subparser: typing.Any) -> None:
        subparser.add_argument(
            "mappings",
            metavar="(<DEV>|<FILE>:<FORMAT>:<SIZE>?):<REPART_DIR>",
            help="A mapping of device to systemd-repart directory, separated by :",
            nargs="+",
        )

    def __call__(
        self, *, parse_result: typing.Any, tmp_dir: str, image_file: str
    ) -> int:
        device_list = parse_arguments(parse_result)
        if not device_list:
            return 1

        for (dev, format, dir) in device_list:
            with create_device(dev, format) as d:
                dev_node = d.device()
                run.run(
                    "/usr/bin/systemd-repart",
                    "--definitions={}".format(dir),
                    "--dry-run=no",
                    "--empty=force",
                    dev_node,
                )

        return 0
