#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The class that drives the system generation.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from . import context
from . import exceptions
from . import parser
from . import run

from enum import Enum, auto, unique
import os
import os.path


@unique
class State(Enum):
    """State of generation process."""

    NEW = auto()
    PARSED = auto()
    GENERATING = auto()
    GENERATED = auto()


class DependencyNode:
    """Node of the dependency tree of all systems."""

    def __init__(self, system, parent, *children):
        """Constructor."""
        self.parent = parent
        self.system = system
        self.state = State.NEW
        self.children = []

    def find(self, system):
        """Find a system in the dependency tree."""
        if self.system == system:
            return self

        for cn in self.children:
            if cn.find(system):
                return cn

        return None


class Generator:
    """Drives the generation of systems."""

    def __init__(self, ctx):
        """Constructor."""
        self._ctx = ctx
        self.systems = []
        self.dependencies = []
        ctx.generator = self

    def _binary(self, selector):
        """Get the full path to a binary."""
        return self._ctx.binary(selector)

    def addSystem(self, system):
        """Add a system to the dependency tree."""
        system_file = os.path.join(self._ctx.systemsDirectory(),
                                   system, system + '.conf')
        if not os.path.exists(system_file):
            raise exceptions.SystemNotFoundError(
                'Could not find systems file for {}, '
                'checked in {}.'.format(system, system_file))

        node = self._find(system)
        if node:
            return node.parent

        base = parser.Parser(self._ctx)

        parentNode = self._find(base)
        node = DependencyNode(system, parentNode)

        if parentNode:
            pass

    def _find(self, system):
        """Find a system in the dependency tree."""
        for d in self.dependencies:
            node = d.find(system)
            if node:
                return node

        return None

    def prepare(self):
        """Prepare for generation."""
        repo_dir = self._ctx.workRepositoryDirectory()
        run_result = run.run(self._ctx,
                             [self._binary(context.Binaries.OSTREE),
                              'init', '--repo={}'.format(repo_dir)])
        if run_result.returncode != 0:
            run.reportCompletedProcess(self._context.print, run_result)
            raise exceptions.PrepareError('Failed to run ostree init.')

    def generate(self):
        """Generate all systems in the dependency tree."""
        pass


if __name__ == '__main__':
    pass
