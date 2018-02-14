#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pretty-print output of cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import sys


def ansify(seq):
    """Use ANSI color codes if possible.

    Use ANSI color codes if possible and strip them out if not.
    """
    if sys.stdout.isatty():
        return seq
    return ''


class Printer:
    """Pretty-print output.

    A Printer will be set up by the cleanroom executable and
    passed on to the cleanroom module.

    The module will then use this Printer object for all its
    output needs.
    """

    def __init__(self, verbose):
        """Constructor."""
        self._verbose = verbose

        self._prefix = '      ' if verbose > 0 else ''

        self._ansi_reset = ansify('\033[0m')
        self._h_prefix = ansify('\033[1;31m')
        self._h1_suffix = ansify('\033[0m\033[1;37m')
        self._error_prefix = ansify('\033[1;31m')
        self._warn_prefix = ansify('\033[1;33m')
        self._ok_prefix = ansify('\033[1;7;32m')
        self._ok_suffix = ansify('\033[0;32m')

        self._ig_fail_prefix = ansify('\033[1;7;33m')
        self._ig_fail_suffix = ansify('\033[0;33m')
        self._fail_prefix = ansify('\033[1;7;31m')
        self._fail_suffix = ansify('\033[0;31m')
        self._extra_prefix = ansify('\033[1;36m')
        self._extra_suffix = ansify('\033[0;m\033[2;m')

    def _print_at_verbosity_level(self, verbosity):
        return verbosity <= self._verbose

    def h1(self, *args, verbosity=0):
        """Print big headline."""
        if not self._print_at_verbosity_level(verbosity):
            return
        intro = '\n\n{}============================================{}'\
                .format(self._h1_suffix, self._ansi_reset)
        prefix = '{}== '.format(self._h1_suffix)
        outro = '{}============================================'\
                .format(self._h1_suffix, self._ansi_reset)
        print(intro)
        print(prefix, *args, self._ansi_reset)
        print(outro)
        print()

    def h2(self, *args, verbosity=0):
        """Print a headline."""
        if not self._print_at_verbosity_level(verbosity):
            return
        intro = '\n{}******{}'.format(self._h_prefix, self._h1_suffix)
        print(intro, *args, self._ansi_reset)

    def h3(self, *args, verbosity=0):
        """Print a subheading."""
        if not self._print_at_verbosity_level(verbosity):
            return
        intro = '\n{}******{}'.format(self._h_prefix, self._ansi_reset)
        print(intro, *args)

    def error(self, *args):
        """Print error message."""
        intro = '{}ERROR:'.format(self._error_prefix)
        print(intro, *args, self._ansi_reset)

    def warn(self, *args):
        """Print warning message."""
        intro = '{}warn: '.format(self._warn_prefix)
        print(intro, *args, self._ansi_reset)

    def success(self, *args, verbosity=0):
        """Print success message."""
        if not self._print_at_verbosity_level(verbosity):
            return

        intro = '{}  OK  {}'.format(self._ok_prefix, self._ok_suffix)
        print(intro, *args, self._ansi_reset)

    def fail(self, ignore, *args, verbosity=0, force_exit=True):
        """Print success message."""
        if not self._print_at_verbosity_level(verbosity):
            return

        if ignore:
            intro = '{} fail {}'.format(self._ig_fail_prefix,
                                        self._ig_fail_suffix)
            print(intro, *args, '(ignored)', self._ansi_reset)
        else:
            intro = '{} FAIL {}'.format(self._fail_prefix, self._fail_suffix)
            print(intro, *args, self._ansi_reset)
            if force_exit:
                sys.exit(1)

    def verbose(self, *args):
        """Print if verbose is set."""
        if not self._print_at_verbosity_level(1):
            return
        print(self._prefix, *args)

    def info(self, *args):
        """Print even more verbose."""
        if not self._print_at_verbosity_level(2):
            return
        intro = '{}......{}'.format(self._extra_prefix, self._extra_suffix)
        print(intro, *args, self._ansi_reset)

    def debug(self, *args):
        """Print if debug is set."""
        if not self._print_at_verbosity_level(3):
            return
        intro = '{}------{}'.format(self._extra_prefix, self._extra_suffix)
        print(intro, *args, self._ansi_reset)

    def trace(self, *args):
        """Print trace messsages."""
        if not self._print_at_verbosity_level(4):
            return
        intro = '{}++++++{}'.format(self._extra_prefix, self._extra_suffix)
        print(intro, *args, self._ansi_reset)
