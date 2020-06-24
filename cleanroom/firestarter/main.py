#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Firestarter binary.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.firestarter.installtarget import InstallTarget

from cleanroom.firestarter.containerfsinstalltarget import (
    ContainerFilesystemInstallTarget,
)
from cleanroom.firestarter.copyinstalltarget import CopyInstallTarget
from cleanroom.firestarter.imagepartitioninstalltarget import (
    ImagePartitionInstallTarget,
)
from cleanroom.firestarter.mountinstalltarget import MountInstallTarget
from cleanroom.firestarter.partitioninstalltarget import PartitionInstallTarget
from cleanroom.firestarter.qemuinstalltarget import QemuInstallTarget
from cleanroom.firestarter.qemuimageinstalltarget import QemuImageInstallTarget
from cleanroom.firestarter.tarballinstalltarget import TarballInstallTarget

from cleanroom.printer import Printer, trace, debug
from cleanroom.firestarter.tools import BorgMount

from argparse import ArgumentParser
import os
import sys
from tempfile import TemporaryDirectory
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
        help="Installation target specifics", dest="subcommand", required=True,
    )
    for it in install_targets:
        debug(
            'Setting up subparser for "{}" with help "{}".'.format(
                it.name, it.help_string
            )
        )
        it.setup_subparser(subparsers.add_parser(it.name, help=it.help_string))

    return parser.parse_args(args[1:])


# Main section:


def main(*command_args: str) -> int:
    known_install_targets: typing.List[InstallTarget] = [
        ContainerFilesystemInstallTarget(),
        CopyInstallTarget(),
        ImagePartitionInstallTarget(),
        MountInstallTarget(),
        PartitionInstallTarget(),
        QemuImageInstallTarget(),
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

    trace("Arguments parsed from command line: {}.".format(parse_result))

    install_target = next(
        x for x in known_install_targets if x.name == parse_result.subcommand
    )
    assert install_target
    debug("Install target {} found.".format(install_target.name))

    with TemporaryDirectory(prefix="fs_{}".format(install_target.name)) as tmp_dir:
        trace("Using temporary directory: {}.".format(tmp_dir))

        image_dir = os.path.join(tmp_dir, "borg")
        os.makedirs(image_dir)

        with BorgMount(
            image_dir,
            system_name=parse_result.system_name,
            repository=parse_result.repository,
            version=parse_result.system_version,
        ) as image_file:
            trace("Mounted borg directory with image file: {}.".format(image_file))
            debug(
                "Running install target with parse_args={}, tmp_dir={} and image_file={}.".format(
                    parse_result, tmp_dir, image_file
                )
            )
            result = install_target(
                parse_result=parse_result, tmp_dir=tmp_dir, image_file=image_file,
            )
            debug("Install target done: return code: {}.".format(result))
            trace("Starting cleanup.")

    trace("Done, leaving with return code {}.".format(result))
    return result


def run():
    current_directory = os.getcwd()

    try:
        result = main(*sys.argv)
    finally:
        os.chdir(current_directory)

    return result
