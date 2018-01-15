#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


class Printer:
    ''' Class to help with output in cleanroom.

    A Printer will be set up by the cleanroom executable and
    passed on to the cleanroom module.

    The module will then use this Printer object for all its
    output needs.
    '''

    def __init__(self, verbose, debug):
        self._verbose = verbose
        self._debug = debug

    def print(self, *args):
        ''' Unconditionally print things. '''
        print(args)

    def verbose(self, *args):
        ''' Print if verbose is set. '''
        if self._verbose: print(args)

    def debug(self, *args):
        ''' Print if debug is set. '''
        if self._debug: print(args)
