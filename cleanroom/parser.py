#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


class Parser:
    ''' Parse a container.conf file '''

    def __init__(self, generator, system, printer):
        self._generator = generator
        self._pr = printer
        self.system = system

        self._pr.verbose('Parser created for {}...'.format(system))

