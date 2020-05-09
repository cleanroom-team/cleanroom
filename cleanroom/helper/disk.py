# -*- coding: utf-8 -*-
"""Helpers for handling discs and partitions.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from __future__ import annotations

from ..exceptions import GenerateError
from ..printer import debug, trace, warn
from .run import run

import collections
import json
import math
import os
import os.path
import subprocess
from re import findall
import stat
import typing
from time import sleep


Disk = collections.namedtuple(
    "Disk",
    [
        "label",
        "id",
        "device",
        "unit",
        "firstlba",
        "lastlba",
        "partitions",
        "sectorsize",
    ],
)
Partition = collections.namedtuple(
    "Partition",
    ["node", "start", "size", "partition_type", "uuid", "name", "sectorsize"],
)


def _is_root() -> bool:
    return os.geteuid() == 0


def is_block_device(path: str) -> bool:
    try:
        stat_info = os.stat(path)
        return stat.S_ISBLK(stat_info.st_mode)
    except os.error:
        return False


def quantify(size: int, block_size: int) -> int:
    quant_size = math.floor(size / block_size)
    if quant_size * block_size != size:
        quant_size += 1
    return quant_size


def kib_ify(size: int) -> int:
    return quantify(size, 1024)


def mib_ify(size: int) -> int:
    return quantify(size, 1024 * 1024)


def byte_size(size: typing.Any) -> int:
    if isinstance(size, int):
        return size

    factor = 1
    if isinstance(size, str):
        unit = size[-1:].lower()
        number_string = size[:-1]
        if unit == "b":
            pass
        elif unit == "k":
            factor = 1024
        elif unit == "m":
            factor = 1024 * 1024
        elif unit == "g":
            factor = 1024 * 1024 * 1024
        elif unit == "t":
            factor = 1024 * 1024 * 1024 * 1024
        elif "0" <= unit <= "9":
            number_string += unit
        else:
            raise ValueError()

        number = int(number_string)
        if number < 0:
            raise ValueError()

        return number * factor

    raise ValueError()


def _sfdisk_size(size: int) -> str:
    return "{}KiB".format(kib_ify(size))


def create_image_file(
    file_name: str, size: int, *, disk_format: str = "qcow2", qemu_img_command: str = ""
) -> None:
    assert _is_root()
    run(
        qemu_img_command or "/usr/bin/qemu-img",
        "create",
        "-q",
        "-f",
        disk_format,
        file_name,
        str(byte_size(size)),
    )


class Device:
    def __init__(self, device: str) -> None:
        assert is_block_device(device)
        self._device = device

        self.wait_for_device_node()

    def __enter__(self) -> typing.Any:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    def device(self, partition: typing.Optional[int] = None) -> str:
        if partition is None:
            return self._device
        return "{}{}".format(self._device, partition)

    def close(self):
        pass

    def wait_for_device_node(self, partition: typing.Optional[int] = None) -> bool:
        dev = self.device(partition)
        trace('Waiting for "{}".'.format(dev))
        for i in range(20):
            if is_block_device(dev):
                return True
            elif os.path.exists(dev):
                warn('"{}" exists but is no block device!'.format(dev))
            sleep(0.5)
        return False


class NbdDevice(Device):
    @staticmethod
    def new_image_file(
        file_name: str,
        size: int,
        *,
        disk_format: str = "qcow2",
        qemu_img_command: str = "",
        qemu_nbd_command: str = "",
        nbd_client_command: str = "",
        sync_command: str = "",
        modprobe_command: str = "",
    ) -> NbdDevice:
        create_image_file(
            file_name, size, disk_format=disk_format, qemu_img_command=qemu_img_command
        )
        debug(
            "New image file {} ({}) created with size {}.".format(
                file_name, disk_format, size
            )
        )
        return NbdDevice(
            file_name,
            disk_format=disk_format,
            qemu_nbd_command=qemu_nbd_command,
            nbd_client_command=nbd_client_command,
            sync_command=sync_command,
            modprobe_command=modprobe_command,
        )

    def __init__(
        self,
        file_name: str,
        *,
        disk_format: str = "qcow2",
        qemu_nbd_command: str = "",
        nbd_client_command: str = "",
        sync_command: str = "",
        modprobe_command: str = "",
    ) -> None:
        assert os.path.isfile(file_name)

        self._file_name = file_name
        self._disk_format = disk_format
        self._qemu_nbd_command = qemu_nbd_command
        self._nbd_client_command = nbd_client_command
        self._sync_command = sync_command

        device = self._create_nbd_block_device(
            file_name,
            disk_format=disk_format,
            qemu_nbd_command=qemu_nbd_command,
            modprobe_command=modprobe_command,
        )
        assert device

        super().__init__(device)

        debug(
            'Block device "{}" created for file {}.'.format(
                self._device, self._file_name
            )
        )

    def __enter__(self) -> typing.Any:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        if self._device:
            run(
                self._sync_command or "/usr/bin/sync"
            )  # make sure changes are synced to disk!
            self._delete_nbd_block_device(self._device, self._qemu_nbd_command)
            self._device = ""

    def device(self, partition: typing.Optional[int] = None) -> str:
        if partition is None:
            return self._device
        return "{}p{}".format(self._device, partition)

    def disk_format(self) -> str:
        return self._disk_format

    def file_name(self) -> str:
        return self._file_name

    # Helpers:

    @staticmethod
    def _create_nbd_block_device(
        file_name: str,
        *,
        disk_format: str = "qcow2",
        qemu_nbd_command: str = "",
        nbd_client_command: str = "",
        modprobe_command: str = "",
    ) -> typing.Optional[str]:
        assert _is_root()
        assert os.path.isfile(file_name)

        if not is_block_device(_nbd_device(0)):
            trace("Loading nbd kernel module...")
            run(modprobe_command or "/usr/bin/modprobe", "nbd")

        for counter in range(257):
            device = _nbd_device(counter)
            counter += 1
            if not is_block_device(device):
                trace("{} is not a block device, aborting".format(device))
                return None

            try:
                result = run(
                    qemu_nbd_command or "/usr/bin/qemu-nbd",
                    "--connect={}".format(device),
                    "--format={}".format(disk_format),
                    file_name,
                    returncode=None,
                    timeout=5,
                    stdout="/dev/null",
                    stderr="/dev/null",
                )
            except subprocess.TimeoutExpired:
                continue

            if result.returncode == 0:
                trace("Device {} connected to file {}.".format(device, file_name))
                return device

        trace("Too many nbd devices found, aborting!")
        return None

    @staticmethod
    def _delete_nbd_block_device(device: str, qemu_nbd_command: str = "") -> None:
        assert _is_root()
        assert is_block_device(device)

        run(qemu_nbd_command or "/usr/bin/qemu-nbd", "--disconnect", device)
        trace('"{}" disconnected.'.format(device))


def _nbd_device(counter: int) -> str:
    return "/dev/nbd" + str(counter)


def _assert_uuid(data: str):
    if (
        len(data) == 32 + 4
        and data[8] == "-"
        and data[13] == "-"
        and data[18] == "-"
        and data[23] == "-"
        and len(findall(r"[a-fA-F0-9]", data)) == 32
    ):
        return

    raise GenerateError('"{}" is not a valid UUID.'.format(data))


class Partitioner:
    def __init__(
        self, device: Device, *, flock_command: str = "", sfdisk_command: str = ""
    ) -> None:
        assert _is_root()
        assert is_block_device(device.device())

        self._flock_command = flock_command or "/usr/bin/flock"
        self._sfdisk_command = sfdisk_command or "/usr/bin/sfdisk"
        self._device = device
        self._data = None  # type: typing.Optional[Disk]

        self._get_partition_data()

    @staticmethod
    def swap_partition(
        *,
        start: typing.Optional[str] = None,
        size: typing.Any = "4G",
        name: str = "swap partition",
    ) -> Partition:
        return Partition(
            node=None,
            start=start,
            size=size,
            sectorsize=512,
            uuid="",
            partition_type="0657fd6d-a4ab-43c4-84e5-0933c84b4f4f",
            name=name,
        )

    @staticmethod
    def efi_partition(
        *, start: typing.Optional[str] = None, size: typing.Any = "512M"
    ) -> Partition:
        return Partition(
            node=None,
            start=start,
            size=size,
            sectorsize=512,
            uuid="",
            partition_type="c12a7328-f81f-11d2-ba4b-00a0c93ec93b",
            name="EFI System Partition",
        )

    @staticmethod
    def data_partition(
        *,
        start: typing.Optional[str] = None,
        size: typing.Any = None,
        partition_type: str = "2d212206-b0ee-482e-9fec-e7c208bef27a",
        partition_uuid: str = "",
        name: str,
    ) -> Partition:
        return Partition(
            node=None,
            start=start,
            size=size,
            sectorsize=512,
            uuid=partition_uuid,
            partition_type=partition_type,
            name=name,
        )

    def is_partitioned(self) -> bool:
        return self._data is not None

    def device(self) -> Device:
        return self._device

    def label(self) -> typing.Optional[str]:
        return self._data.label if self._data else None

    def id(self) -> typing.Optional[str]:
        return self._data.id if self._data else None

    def first_lba(self) -> typing.Optional[int]:
        return self._data.firstlba if self._data else None

    def last_lba(self) -> typing.Optional[int]:
        return self._data.lastlba if self._data else None

    def partitions(self) -> typing.Optional[typing.List[Partition]]:
        return self._data.partitions if self._data else None

    def repartition(self, partitions: typing.List[Partition]) -> None:
        instructions = "label: gpt\n"
        for p in partitions:
            assert isinstance(p, Partition)

            prefix = ""
            partition_data: typing.List[str] = []
            if p.node is not None:
                prefix = "{}: ".format(p.node)
            if p.start is not None:
                partition_data.append(
                    "start={}".format(_sfdisk_size(byte_size(p.start)))
                )
            if p.size is not None:
                partition_data.append("size={}".format(_sfdisk_size(byte_size(p.size))))
            if p.partition_type:
                _assert_uuid(p.partition_type)
                partition_data.append('type="{}"'.format(p.partition_type))
            if p.uuid:
                _assert_uuid(p.uuid)
                partition_data.append('uuid="{}"'.format(p.uuid))
            if p.name:
                partition_data.append('name="{}"'.format(p.name))

            instructions += prefix + ", ".join(partition_data) + "\nprint\n"

        trace("SFDISK partition instructions:\n{}---EOF---".format(instructions))

        run(
            self._flock_command,
            self._device.device(),
            self._sfdisk_command,
            "--color=never",
            self._device.device(),
            trace_output=trace,
            input=instructions.encode("utf-8"),
        )

        trace("SFDISK done.")

        for i in range(len(partitions)):
            assert self._device.wait_for_device_node(partition=i + 1)

        self._get_partition_data()

    def _get_partition_data(self) -> None:
        # FIXME: The sizes/start information is pretty useless.
        #        It is given in sectors, but there is no information
        #        how big such a sector actually is. Assuming 512 bytes
        #        no longer seems safe with 4K sector drives...
        result = run(
            self._flock_command,
            self._device.device(),
            self._sfdisk_command,
            "--color=never",
            "--json",
            self._device.device(),
            returncode=None,
        )
        if result.returncode != 0:
            self._data = None
        else:
            json_data = json.loads(result.stdout)
            self._data = Disk(**json_data["partitiontable"])
            assert self._data.device == self._device.device()
