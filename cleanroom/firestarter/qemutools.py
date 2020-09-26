#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Qemu related tool functions.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.firestarter.tools as tools
import os
from shutil import copyfile
import typing


def _append_network(
    hostname: str,
    *,
    hostfwd: typing.List[str] = [],
    mac: str = "",
    net: str = "",
    host: str = "",
):
    hostfwd_args = [f"hostfwd={p}" for p in hostfwd]

    hostfwd_str = "," + ",".join(hostfwd_args) if hostfwd_args else ""
    mac_str = f",mac={mac}" if mac else ""
    host_str = f",host={host}" if host else ""
    net_str = f",net={net}" if net else ""

    # -netdev bridge,id=bridge1,br=qemubr0
    # -device virtio-net,netdev=bridge1,mac=52:54:00:12:01:c1

    return [
        "-netdev",
        f"user,id=nic0,hostname={hostname}{hostfwd_str}{net_str}{host_str}",
        "-device",
        f"virtio-net,netdev=nic0{mac_str}",
    ]


def _append_hdd(bootindex: int, counter: int, disk: str):
    disk_parts = disk.split(":")
    usb_disk = "usb" in disk_parts
    read_only = "read-only" in disk_parts
    if usb_disk:
        disk_parts.remove("usb")
    if read_only:
        disk_parts.remove("read-only")

    if len(disk_parts) < 2:
        disk_parts.append("qcow2")
    assert len(disk_parts) == 2

    c = counter

    driver = "virtio-blk-pci"
    if usb_disk:
        driver = "usb-storage"

    drive_extra = ""
    if read_only:
        drive_extra += ",read-only"

    return [
        "-drive",
        f"file={disk_parts[0]},format={disk_parts[1]},if=none,id=disk{c}{drive_extra}",
        "-device",
        f"{driver},drive=disk{c},bootindex={bootindex}",
    ]


def _append_fs(fs: str, *, read_only: bool = False):
    fs_parts = fs.split(":")
    assert len(fs_parts) == 2

    ro = ",read-only" if read_only else ""

    return [
        "-virtfs",
        f"local,id={fs_parts[0]},path={fs_parts[1]},mount_tag={fs_parts[0]},security_mode=passthrough{ro}",
    ]


def _append_efi(efi_vars: str):
    if not os.path.exists(efi_vars):
        copyfile("/usr/share/ovmf/x64/OVMF_VARS.fd", efi_vars)
    return [
        "-drive",
        "if=pflash,format=raw,readonly," "file=/usr/share/ovmf/x64/OVMF_CODE.fd",
        "-drive",
        f"if=pflash,format=raw,file={efi_vars}",
    ]


def setup_parser_for_qemu(parser: typing.Any) -> None:
    parser.add_argument(
        "--bios", dest="use_bios", action="store_true", help="Use BIOS over EFI"
    )

    parser.add_argument(
        "--no-graphic",
        dest="no_graphic",
        action="store_true",
        help="Use no-graphics mode",
    )

    parser.add_argument(
        "--cores", action="store", nargs="?", default=2, help="Number of cores to use."
    )
    parser.add_argument(
        "--memory", action="store", nargs="?", default="4G", help="Memory"
    )
    parser.add_argument(
        "--mac",
        dest="mac",
        action="store",
        nargs="?",
        default="",
        help="MAC address of main network card",
    )
    parser.add_argument(
        "--net",
        dest="net",
        action="store",
        nargs="?",
        default="",
        help="Network address of main network card",
    )
    parser.add_argument(
        "--host",
        dest="host",
        action="store",
        nargs="?",
        default="",
        help="Host address of main network card",
    )

    parser.add_argument(
        "--hostname",
        dest="hostname",
        action="store",
        nargs="?",
        default="unknown",
        help="Hostname to use for NIC",
    )
    parser.add_argument(
        "--hostfwd",
        dest="hostfwd",
        default=[],
        action="append",
        help="Port spec to forward from host to guest",
    )

    parser.add_argument(
        "--disk",
        dest="disks",
        default=[],
        action="append",
        help="Extra disks to add (file[:format])",
    )

    parser.add_argument(
        "--ro-fs",
        dest="ro_fs_es",
        default=[],
        action="append",
        help="Host folders to make available to guest -- " "read-only (id:path)",
    )
    parser.add_argument(
        "--fs",
        dest="fs_es",
        default=[],
        action="append",
        help="Host folder to make available to guest (id:path)",
    )

    parser.add_argument(
        "--verbatim",
        dest="verbatim",
        action="append",
        help="Argument to copy verbatim to qemu.",
    )


def run_qemu(
    parse_result: typing.Any, *, drives: typing.List[str] = [], work_directory: str
) -> int:
    qemu_args = [
        "/usr/bin/qemu-system-x86_64",
        "--enable-kvm",
        "-cpu",
        "Penryn",  # Needed for clover to boot:-/
        "-smp",
        f"cores={parse_result.cores}",
        "-machine",
        "pc-q35-2.12",
        "-m",
        f"size={parse_result.memory}",  # memory
        "-object",
        "rng-random,filename=/dev/urandom,id=rng0",
        "-device",
        "virtio-rng-pci,rng=rng0,max-bytes=512,period=1000",
        # Random number generator
        "-usb",
    ]

    qemu_args += _append_network(
        parse_result.hostname,
        hostfwd=parse_result.hostfwd,
        mac=parse_result.mac,
        net=parse_result.net,
        host=parse_result.host,
    )

    boot_index = 0
    hdd_counter = 0
    for disk in drives:
        qemu_args += _append_hdd(boot_index, hdd_counter, disk)
        boot_index += 1
        hdd_counter += 1
    for disk in parse_result.disks:
        qemu_args += _append_hdd(boot_index, hdd_counter, disk)
        boot_index += 1
        hdd_counter += 1

    for fs in parse_result.ro_fs_es:
        qemu_args += _append_fs(fs, read_only=True)
    for fs in parse_result.fs_es:
        qemu_args += _append_fs(fs, read_only=False)

    if parse_result.no_graphic:
        qemu_args.append("-nographic")

    if not parse_result.use_bios:
        qemu_args += _append_efi(os.path.join(work_directory, "vars.fd"))

    if parse_result.verbatim:
        qemu_args += parse_result.verbatim

    run_str = '" "'.join(qemu_args)
    print(f'Running: "{run_str}"')
    result = tools.run(*qemu_args, work_directory=work_directory, check=False)

    if result.returncode != 0:
        print(f"Qemu run Failed with return code {result.returncode}.")
        print(f"Qemu stdout: {result.stdout}")
        print(f"Qemu stderr: {result.stderr}")

    return result.returncode
