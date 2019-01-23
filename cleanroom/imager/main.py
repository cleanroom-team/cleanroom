#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CleanRoom functionality.

FIXME: Allow for different distro ids

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from ..printer import Printer
from .imager import *

from argparse import ArgumentParser
import sys


def _parse_commandline(*arguments: str):
    """Parse the command line options."""
    parser = ArgumentParser(description='Cleanroom OS image writer',
                            prog=arguments[0])
    parser.add_argument('--verbose', action='count', default=0,
                        help='Be verbose')

    parser.add_argument('--repository', dest='repository', action='store',
                        help='Borg repository to extract filesystems from.')

    parser.add_argument('--force', dest='force', action='store_true',
                        help='Overwrite existing image file.')
    parser.add_argument('--repartition', dest='repartition', action='store_true',
                        help='Repartition device or file.')

    parser.add_argument('--efi-size', dest='efi_size', action='store',
                        nargs='?', default='0',
                        help='Size of EFI partition (defaults to minimum).')
    parser.add_argument('--swap-size', dest='swap_size', action='store',
                        nargs='?', default='512M',
                        help='Size of swap partition (0 to avoid creation).')
    parser.add_argument('--extra-partition', dest='extra_partitions',
                        default=[], action='append',
                        help='Add an extra partition (SIZE:FILESYSTEM:LABEL:TARBALL).')

    parser.add_argument('--image-format', dest='disk_format', action='store',
                        default='qcow2', nargs='?',
                        help='The format of the image file to generate_systems.')

    parser.add_argument('--timestamp', dest='timestamp', action='store',
                        nargs='?', default=None,
                        help='Timestamp of system to install (latest if none given).')

    parser.add_argument(dest='system',  metavar='<system>',
                        help='system to turn into an image.')

    parser.add_argument(dest='image', metavar='<image>',
                        help='name of the image file or device. "XXXXXX" will be replaced by timestamp.')

    parse_result = parser.parse_args(arguments[1:])

    return parse_result


def run() -> None:
    """Run image installer with command line arguments."""
    main(*sys.argv)


def main(*args: str):
    """Run image installer with arguments."""
    args = _parse_commandline(*args)

    if not args.system:
        print('No system to process.')
        sys.exit(1)

    if not args.repository:
        print('No repository given.')
        sys.exit(2)

    # Set up printing:
    pr = Printer.instance()
    pr.set_verbosity(args.verbose)
    pr.show_verbosity_level()

    success('Setup done.', verbosity=4)

    extra_partitions = parse_extra_partitions(args.extra_partitions)

    system = args.system
    image_config = ImageConfig(args.image, args.disk_format, args.force, args.repartition,
                               disk.mib_ify(disk.normalize_size(args.efi_size)),
                               disk.mib_ify(disk.normalize_size(args.swap_size)),
                               extra_partitions)

    trace('Validating inputs.')
    validate_image_config_path(image_config.path, image_config.force)

    path = image_config.path

    try:
        root_only_part(image_config, system, args.timestamp, args.repository)
    except Exception as e:
        fail('Failed to create image: {}'.format(str(e)))
        raise e
    finally:
        pr.flush()

    success('Image file {} created.'.format(path), verbosity=0)
