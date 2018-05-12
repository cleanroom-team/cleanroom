#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CleanRoom functionality.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from .context import Context
from .generator import Generator
from .parser import Parser
from .preflight import preflight_check
from .workdir import WorkDir

from ..printer import (debug, fail, info, Printer, success, trace, verbose,)
from ..exceptions import (GenerateError, PreflightError, PrepareError,)

from argparse import ArgumentParser
import os
import sys


def _parse_commandline(arguments):
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

    parser.add_argument('--export-repository', dest='export_repository',
                        action='store',
                        help='Borg repository to export created filesystems '
                        'into.')

    parser.add_argument('--clear-work-directory', dest='clear_work_directory',
                        action='store_true',
                        help='Clear the work directory before proceeding.')
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


def run():
    """Run cleanroom with command line arguments."""
    main(*sys.argv)


def main(*args):
    """Run cleanroom with arguments."""
    old_work_directory = os.getcwd()

    args = _parse_commandline(args)

    if not args.list_commands and not args.systems:
        print('No systems to process.')
        sys.exit(1)

    if not args.export_repository:
        print('No export repository given.')
        sys.exit(2)

    # Set up printing:
    pr = Printer.Instance()
    pr.set_verbosity(args.verbose)

    _log_verbosity_level()

    # Set up global context object:
    ctx = Context(export_repository=args.export_repository,
                  ignore_errors=args.ignore_errors,
                  keep_temporary_data=args.keep_temporary_data)

    # Run pre-flight checks:
    _preflight_check(ctx)

    systems_directory = args.systems_directory \
        if args.systems_directory else os.getcwd()

    with WorkDir(ctx, work_directory=args.work_directory,
                 clear_work_directory=args.clear_work_directory,
                 clear_storage=args.clear_storage) as work_directory:
        ctx.set_directories(systems_directory, work_directory)

        # Find commands:
        Parser.find_commands(ctx.systems_commands_directory(),
                             ctx.commands_directory())

        try:
            _generate(ctx, args.systems)
        finally:
            os.chdir(old_work_directory)


def _preflight_check(ctx):
    try:
        preflight_check(ctx)
    except PreflightError:
        fail('Preflight Check failed', ignore=ctx.ignore_errors)
        if not ctx.ignore_errors:
            raise
    else:
        success('Preflight Check passed', verbosity=2)


def _generate(ctx, systems):
    generator = Generator(ctx)

    try:
        generator.prepare()
    except PrepareError as e:
        fail('Preparation failed: {}'.format(e))
        raise
    else:
        success('Preparation phase.', verbosity=2)

    for s in systems:
        if s.endswith('.def'):
            s = s[:-4]
        generator.add_system(s)

    try:
        generator.generate()
    except GenerateError as e:
        fail('Generation failed: {}'.format(e))
        raise
    else:
        success('Generation phase.', verbosity=2)


def _log_verbosity_level():
    verbose('Verbose output enabled.')
    info('Info output enabled.')
    debug('Debug output enabled.')
    trace('Trace output enabled.')
