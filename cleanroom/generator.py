#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from . import context
from . import exceptions
from . import parser
from . import run

from enum import Enum, auto, unique
import os
import os.path
import subprocess


@unique
class State(Enum):
    NEW = auto()
    PARSED = auto()
    GENERATING = auto()
    GENERATED = auto()


class DependencyNode:
    def __init__(self, system, parent, *children):
        self.parent = parent
        self.system = system
        self.state = State.NEW
        self.children = []

    def find(self, system):
        if self.system == system:
            return self

        for cn in children:
            if cn.find(system):
                return cn

        return None


class Generator:
    def __init__(self, ctx):
        self._ctx = ctx
        self.systems = []
        self.dependencies = []
        ctx.generator = self

    def _binary(self, selector):
        return self._ctx.binary(selector)

    def addSystem(self, system):
        system_file = os.path.join(self._ctx.systemsDirectory(), system, system + '.conf')
        if not os.path.exists(system_file):
            raise exceptions.SystemNotFoundError('Could not find systems file for {}, checked in {}.'.format(system, system_file))

        node = self._find(system)
        if node:
            return node.parent

        base = parser.Parser(self._ctx)

        parentNode = self._find(base)
        node = DependencyNode(system, parentNode)

        if parentNode:
            pass

    def _find(self, system):
        for d in self.dependencies:
            node = d.find(system)
            if node:
                return node

        return None


    def prepare(self):
        repo_dir = self._ctx.workRepositoryDirectory()
        run_result = run.run(self._ctx,
                         [self._binary(context.Binaries.OSTREE), 'init', '--repo={}'.format(repo_dir)])
        if run_result.returncode != 0:
            reportCompletedProcess(self._context.print, run_result)
            raise exceptions.PrepareError('Failed to run ostree init.')

    def generate(self):
        pass


if __name__ == '__main__':
    pass
