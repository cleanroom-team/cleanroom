#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CleanRoom functionality.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from .binarymanager import Binaries, BinaryManager
from .commandmanager import CommandManager
from .exceptions import PreflightError
from .generator import Generator
from .helper.btrfs import BtrfsHelper
from .preflight import preflight_check
from .printer import fail, Printer, success
from .workdir import WorkDir
from .systemsmanager import SystemsManager

from argparse import ArgumentParser
import os
import sys
import typing


def _parse_commandline(*arguments: str) -> typing.Any:
    """Parse the command line options."""
    parser = ArgumentParser(description='Cleanroom OS image script generator',
                            prog=arguments[0])
    parser.add_argument('--verbose', action='count', default=0,
                        help='Be verbose')
    parser.add_argument('--list-commands', dest='list_commands',
                        action='store_true',
                        help='List known commands for definition files')

    parser.add_argument('--ignore-errors', dest='ignore_errors',
                        action='store_true',
                        help='Force continuation on non-critical errors.')

    parser.add_argument('--systems-directory', dest='systems_directory',
                        action='store',
                        help='Directory containing system definitions')
    parser.add_argument('--work-directory', dest='work_directory',
                        action='store', help='Work area to create files in')

    parser.add_argument('--clear-scratch-directory', dest='clear_scratch_directory',
                        action='store_true',
                        help='Clear the scratch directory before proceeding.')
    parser.add_argument('--clear-storage', dest='clear_storage',
                        action='store_true',
                        help='Clear the storage before proceeding.')
    parser.add_argument('--keep-temporary-data', dest='keep_temporary_data',
                        action='store_true',
                        help='Keep temporary data in work directory.')

    parser.add_argument(dest='systems', nargs='*', metavar='<system>',
                        help='systems to create')

    parse_result = parser.parse_args(arguments[1:])

    return parse_result


def _preflight_check(func: typing.Callable[[], None], *,
                     ignore_errors=False) -> None:
    try:
        func()
    except PreflightError:
        fail('Preflight Check failed', ignore=ignore_errors)
        if not ignore_errors:
            raise
    else:
        success('Preflight Check passed', verbosity=2)


def run() -> None:
    """Run cleanroom with command line arguments."""
    current_directory = os.getcwd()

    try:
        main(*sys.argv)
    finally:
        os.chdir(current_directory)


def main(*command_arguments: str) -> None:
    """Run cleanroom with arguments."""
    args = _parse_commandline(*command_arguments)

    if not args.list_commands and not args.systems:
        print('No systems to process.')
        sys.exit(1)

    # Set up printing:
    pr = Printer.instance()
    pr.set_verbosity(args.verbose)
    pr.show_verbosity_level()

    # Find binaries:
    binary_manager = BinaryManager()

    # Run pre-flight checks:
    btrfs_helper = BtrfsHelper(binary_manager.binary(Binaries.BTRFS))

    _preflight_check(lambda: preflight_check(binary_manager),
                     ignore_errors=args.ignore_errors)

    systems_directory = args.systems_directory \
        if args.systems_directory else os.getcwd()

    command_manager \
        = CommandManager(os.path.join(os.path.dirname(__file__), 'commands'),
                         os.path.join(systems_directory, 'cleanroom/commands'),
                         btrfs_helper=btrfs_helper,
                         binary_manager=binary_manager)

    _preflight_check(lambda: command_manager.preflight_check(),
                     ignore_errors=args.ignore_errors)

    if args.list_commands:
        command_manager.print_commands()
        exit(0)

    with WorkDir(btrfs_helper,
                 work_directory=args.work_directory,
                 clear_scratch_directory=args.clear_scratch_directory,
                 clear_storage=args.clear_storage) as work_directory:

        systems_manager \
            = SystemsManager(command_manager, systems_directory,
                             *args.systems)

        generator = Generator(systems_manager)
        generator.generate_systems(work_directory=work_directory,
                                   command_manager=command_manager,
                                   ignore_errors=args.ignore_errors)
