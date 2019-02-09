#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CleanRoom binary.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from argparse import ArgumentParser
from collections import namedtuple
import os
import sys
import typing


InstallTypes = namedtuple('InstallTypes', ['help_string', 'execute'])


# Helper code:


def _parse_commandline(*args: str,
                       install_types: typing.Dict[str, InstallTypes]) \
        -> typing.Any:
    """Parse the command line options."""
    parser = ArgumentParser(description='Cleanroom OS image fire starter',
                            prog=args[0])

    parser.add_argument('--repository', dest='repository',
                        action='store',
                        help='The repository of systems to work with.')
    parser.add_argument('--install-type', dest='install_type',
                        action='store', help='The type of installation to do.')

    parser.add_argument(dest='system_name', nargs='+', metavar='<system>',
                        help='system to install')

    parse_result = parser.parse_args(args[1:])

    if not parse_result.repository:
        print('No repository to take the system from.')
        sys.exit(1)

    if parse_result.install_type not in install_types:
        print('Unknown installation type "{}".'
              .format(parse_result.install_type))
        print('Known installation types are:')
        for k, i in install_types.items():
            print('    {}: {}'.format(k, i['help_string']))
        sys.exit(1)

    return parse_result


# Install types:

def image_directory(*args):
    print("Installing image directory!")


def run_in_qemu(*args):
    print("Running in qemu!")


# Main section:

def main(*command_args: str):
    known_install_types: typing.Dict[str, InstallTypes] \
        = {'image_directory':
               InstallTypes(help_string='Install image into an image directory',
                            execute=image_directory),
           'vm_runner':
               InstallTypes(help_string='Start image in qemu.',
                            execute=run_in_qemu),
           }

    parse_result = _parse_commandline(*command_args,
                                      install_types=known_install_types)

    known_install_types[parse_result.install_type]['execute'](parse_result)


def run():
    current_directory = os.getcwd()

    try:
        main(*sys.argv)
    finally:
        os.chdir(current_directory)


if __name__ == '__main__':
    run()
