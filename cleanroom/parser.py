#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


class Parser:
    ''' Parse a container.conf file '''

    def __init__(self, system, ctx):
        self._context = ctx

        built_in_command_path = command.__file__
        self._pr.verbose('Parser created for {}...'.format(system))

