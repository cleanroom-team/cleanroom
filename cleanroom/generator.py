# -*- coding: utf-8 -*-
"""The class that drives the system generation.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.exceptions as exceptions
import cleanroom.executor as executor
import cleanroom.parser as parser
import cleanroom.printer as printer
import cleanroom.systemcontext as systemcontext

import datetime
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

    def _binary(self, selector):
        """Get the full path to a binary."""
        return self._ctx.binary(selector)

    def add_system(self, system):
        """Add a system to the dependency tree."""
        if not system:
            return None

        printer.debug('Adding system "{}".'
                      .format(system if system else "<NONE>"))

        node = self._find(system)
        if node:
            printer.trace('Found system "{}" in system_forest.'.format(system))
            return node

        system_file = self._find_system_definition_file(system)
        (base_system, command_list) \
            = self._parse_system_definition_file(system_file)

        printer.trace('"{}" depends on "{}"'.format(system, base_system))
        parent_node = self.add_system(base_system)
        node = DependencyNode(system, parent_node, command_list)

        if parent_node:
            parent_node.children.append(node)
        else:
            self._systems_forest.append(node)

        return node

    def _parse_system_definition_file(self, system_file):
        printer.trace('Parsing "{}".'.format(system_file))
        system_parser = parser.Parser()
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
        printer.debug('Systems forest ({} trees):'
                      .format(len(self._systems_forest)))
        for node in self._walk_systems_forest():
            printer.debug('  {}{} ({} children)'
                          .format(base_indent * node.depth(), node.system,
                                  len(node.children)))

    def _walk_systems_forest(self):
        for root_node in self._systems_forest:
            for node in root_node.walk():
                yield node

    def prepare(self):
        """Prepare for generation."""
        printer.h2('Preparing for system generation')
        if not os.path.exists(self._ctx.storage_directory()):
            os.makedirs(self._ctx.storage_directory())

    def generate(self):
        """Generate all systems in the dependency tree."""
        self._print_systems_forest()
        timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

        for node in self._walk_systems_forest():
            system = node.system
            command_list = node.command_list

            printer.h1('Generate "{}"'.format(system))
            try:
                system_context \
                    = systemcontext.SystemContext(self._ctx,
                                                  system=system,
                                                  timestamp=timestamp)
                if os.path.isdir(system_context.storage_directory()):
                    printer.verbose('Taking from storage.')
                else:
                    exe = executor.Executor()
                    exe.run(system_context, system, command_list)
            except AssertionError as e:
                printer.fail('Generation of "{}" asserted.'
                             .format(system,), force_exit=False,
                             ignore=self._ctx.ignore_errors)
                if not self._ctx.ignore_errors:
                    raise
            except Exception as e:
                printer.fail('Generation of "{}" failed: {}.'
                             .format(system, e), force_exit=False,
                             ignore=self._ctx.ignore_errors)
                if not self._ctx.ignore_errors:
                    raise
            else:
                printer.success('Generation of "{}" complete.'.format(system))
