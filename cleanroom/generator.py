#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The class that drives the system generation.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from . import context
from . import executor
from . import exceptions
from . import parser
from . import run

import os
import os.path


class DependencyNode:
    """Node of the dependency tree of all systems."""

    def __init__(self, system, parent, command_list):
        """Constructor."""
        # Tree:
        self.parent = parent
        self.children = []

        # Payload:
        self.system = system
        self.command_list = command_list

        assert(system)
        assert(len(command_list) >= 2)  # At least _setup and _teardown!

    def find(self, system):
        """Find a system in the dependency tree."""
        if self.system == system:
            return self

        for cn in self.children:
            if cn.find(system):
                return cn

        return None

    def walk(self):
        """Walk the nodes in pre-order."""
        yield(self)

        for child in self.children:
            for node in child.walk():
                yield node

    def depth(self):
        """Calculate the distance from the root node."""
        if self.parent:
            return self.parent.depth() + 1
        return 0


class Generator:
    """Drives the generation of systems."""

    def __init__(self, ctx):
        """Constructor."""
        self._ctx = ctx
        self._systems_forest = []
        ctx.generator = self

    def _binary(self, selector):
        """Get the full path to a binary."""
        return self._ctx.binary(selector)

    def add_system(self, system):
        """Add a system to the dependency tree."""
        if not system:
            return None

        self._ctx.printer.debug('Adding system "{}".'
                                .format(system if system else "<NONE>"))

        node = self._find(system)
        if node:
            self._ctx.printer.trace('Found system "{}" in system_forest.'
                                    .format(system))
            return node

        system_file = self._find_system_definition_file(system)
        (base_system, command_list) \
            = self._parse_system_definition_file(system_file)

        self._ctx.printer.trace('"{}" is based on "{}"'
                                .format(system, base_system))
        parent_node = self.add_system(base_system)
        node = DependencyNode(system, parent_node, command_list)

        if parent_node:
            parent_node.children.append(node)
        else:
            self._systems_forest.append(node)

        return node

    def _parse_system_definition_file(self, system_file):
        self._ctx.printer.trace('Parsing "{}".'.format(system_file))
        system_parser = parser.Parser(self._ctx)
        command_list = []
        for command in system_parser.parse(system_file):
            command_list.append(command)

        base_system = ''
        for exec_object in command_list:
            if exec_object.dependency():
                base_system = exec_object.dependency()
                break

        return (base_system, command_list)

    def _find_system_definition_file(self, system):
        """Make sure a system definition file can be found."""
        system_file = os.path.join(self._ctx.systems_directory(),
                                   system + '.def')
        if not os.path.exists(system_file):
            raise exceptions.SystemNotFoundError(
                'Could not find systems file for {}, '
                'checked in {}.'.format(system, system_file))

        return system_file

    def _find(self, system):
        """Find a system in the dependency tree."""
        for root_node in self._systems_forest:
            node = root_node.find(system)
            if node:
                return node

        return None

    def _print_systems_forest(self):
        """Print the systems forest."""
        base_indent = "  "
        self._ctx.printer.debug('Systems forest ({} trees):'
                                .format(len(self._systems_forest)))
        for node in self._walk_systems_forest():
            self._ctx.printer.debug('  {}{} ({} children)'
                                    .format(base_indent * node.depth(),
                                            node.system,
                                            len(node.children)))

    def _walk_systems_forest(self):
        for root_node in self._systems_forest:
            for node in root_node.walk():
                yield node

    def prepare(self):
        """Prepare for generation."""
        repo_dir = self._ctx.work_repository_directory()
        run.run(self._ctx, [self._binary(context.Binaries.OSTREE),
                'init', '--repo={}'.format(repo_dir)], exit_code=0)

    def generate(self):
        """Generate all systems in the dependency tree."""
        self._print_systems_forest()

        for node in self._walk_systems_forest():
            system = node.system
            command_list = node.command_list

            self._ctx.printer.h1('Generate "{}"'.format(system))
            try:
                exe = executor.Executor()
                exe.run(self._ctx, system, command_list)
            except Exception as e:
                self._ctx.printer.fail(self._ctx.ignore_errors,
                                       'Generation of "{}" failed: {}.'
                                       .format(system, e),
                                       force_exit=False)
                if not self._ctx.ignore_errors:
                    raise
            else:
                self._ctx.printer.success('Generation of "{}" complete.'
                                          .format(system))


if __name__ == '__main__':
    pass
