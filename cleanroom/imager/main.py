#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CleanRoom functionality.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from ..printer import (debug, fail, info, Printer, success, trace, verbose,)

from argparse import ArgumentParser
import os
import sys


def _parse_commandline(arguments):
    """Parse the command line options."""
    parser = ArgumentParser(description='Cleanroom OS image writer',
                            prog=arguments[0])
    parser.add_argument('--verbose', action='count', default=0,
                        help='Be verbose')

    parser.add_argument('--repository', dest='repository',
                        action='store',
                        help='Borg repository to extract filesystems from.')

    parser.add_argument('--keep-temporary-data', dest='keep_temporary_data',
                        action='store_true',
                        help='Keep temporary data in work directory.')

    parser.add_argument(dest='systems', nargs='*', metavar='<system>',
                        help='systems to create')

    parse_result = parser.parse_args(arguments[1:])

    return parse_result


def run():
    """Run image installer with command line arguments."""
    main(*sys.argv)


def main(*args):
    """Run image installer with arguments."""
    old_work_directory = os.getcwd()

    args = _parse_commandline(args)

    if not args.systems:
        print('No systems to process.')
        sys.exit(1)

    if not args.repository:
        print('No repository given.')
        sys.exit(2)

    # Set up printing:
    pr = Printer.Instance()
    pr.set_verbosity(args.verbose)
    pr.show_verbosity_level()
