#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from argparse import ArgumentParser
import sys

def parse_commandline(arguments):
    '''This function parses the command line options.
    '''
    parser = ArgumentParser(description='Cleanroom OS image script generator',
                            prog=arguments[0])
    parser.add_argument('--debug', dest='debug', action='store_true',
                        help='Show debug information')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help='Be verbose')

    parser.add_argument('--workdir', dest='work_dir', action='store',
                        help='Work area to create files in')

    parser.add_argument(dest='systems', action='append', nargs='+',
                        metavar='<system>', help='systems to create')

    parse_result = parser.parse_args(arguments[1:])

    return parse_result


args = parse_commandline(sys.argv)

print('workdir: {}'.format(args.work_dir))
print('systems: {}'.format(args.systems))

