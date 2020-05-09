#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Firestarter binary.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.firestarter.imagepartitioninstalltarget import (
    ImagePartitionInstallTarget,
)
from cleanroom.firestarter.installtarget import InstallTarget
from cleanroom.firestarter.containerfsinstalltarget import (
    ContainerFilesystemInstallTarget,
)
from cleanroom.firestarter.directoryinstalltarget import DirectoryInstallTarget
from cleanroom.firestarter.mountinstalltarget import MountInstallTarget
from cleanroom.firestarter.qemubootinstalltarget import QemuBootInstallTarget
from cleanroom.firestarter.qemuinstalltarget import QemuInstallTarget
from cleanroom.firestarter.tarballinstalltarget import TarballInstallTarget
from cleanroom.printer import Printer

from argparse import ArgumentParser
import os
import sys
import typing


# Helper code:


def _parse_commandline(
    *args: str, install_targets: typing.List[InstallTarget]
) -> typing.Any:
    """Parse the command line options."""
    parser = ArgumentParser(description="Cleanroom OS image fire starter", prog=args[0])

    parser.add_argument("--verbose", action="count", default=0, help="Be verbose")

    parser.add_argument(
        "--repository",
        dest="repository",
        type=str,
        action="store",
        required=True,
        help="The repository of systems to work with.",
    )

    parser.add_argument(
        dest="system_name", metavar="<system>", type=str, help="system to install"
    )
    parser.add_argument(
        "--system-version",
        dest="system_version",
        default="",
        type=str,
        help="version of system to install.",
    )

    subparsers = parser.add_subparsers(
        help="Installation target specifics", dest="target_type"
    )
    for it in install_targets:
        it.setup_subparser(subparsers.add_parser(it.name, help=it.help_string))

    return parser.parse_args(args[1:])


# Main section:


def main(*command_args: str):
    known_install_targets = [
        ContainerFilesystemInstallTarget(),
        DirectoryInstallTarget(),
        ImagePartitionInstallTarget(),
        MountInstallTarget(),
        QemuBootInstallTarget(),
        QemuInstallTarget(),
        TarballInstallTarget(),
    ]

    parse_result = _parse_commandline(
        *command_args, install_targets=known_install_targets
    )

    # Set up printing:
    pr = Printer.instance()
    pr.set_verbosity(parse_result.verbose)
    pr.show_verbosity_level()

    install_target = next(
        x for x in known_install_targets if x.name == parse_result.target_type
    )
    install_target(parse_result)


def run():
    current_directory = os.getcwd()

    try:
        main(*sys.argv)
    finally:
        os.chdir(current_directory)
