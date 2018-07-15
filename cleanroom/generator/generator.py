# -*- coding: utf-8 -*-
"""The class that drives the system generation.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .executor import Executor
from .parser import Parser
from .systemcontext import SystemContext

from ..exceptions import (SystemNotFoundError, GenerateError,)
from ..printer import (debug, fail, h1, h2, success, trace, verbose, Printer,)

import datetime
import os
import os.path
import traceback


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

        debug('Adding system "{}".'.format(system if system else "<NONE>"))

        node = self._find(system)
        if node:
            trace('Found system "{}" in system_forest.'.format(system))
            return node

        system_file = self._find_system_definition_file(system)
        (base_system, command_list) \
            = self._parse_system_definition_file(system_file)

        trace('"{}" depends on "{}"'.format(system, base_system))
        parent_node = self.add_system(base_system)
        node = DependencyNode(system, parent_node, command_list)

        if parent_node:
            parent_node.children.append(node)
        else:
            self._systems_forest.append(node)

        return node

    def _parse_system_definition_file(self, system_file):
        trace('Parsing "{}".'.format(system_file))
        system_parser = Parser()
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
            raise SystemNotFoundError('Could not find systems file for {}, checked in {}.'
                                      .format(system, system_file))

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
        debug('Systems forest ({} trees):'.format(len(self._systems_forest)))
        for node in self._walk_systems_forest():
            debug('  {}{} ({} children)'.format(base_indent * node.depth(),
                                                node.system, len(node.children)))

    def _walk_systems_forest(self):
        for root_node in self._systems_forest:
            for node in root_node.walk():
                yield node

    def prepare(self):
        """Prepare for generation."""
        h2('Preparing for system generation')
        if not os.path.exists(self._ctx.storage_directory()):
            os.makedirs(self._ctx.storage_directory())

    def _report_error(self, system, exception, ignore_errors=False):
        if isinstance(exception, AssertionError):
            fail('Generation of "{}" asserted.'.format(system), force_exit=False)
        else:
            fail('Generation of "{}" failed: {}'.format(system, str(exception)),
                 force_exit=False)

        self._report_error_details(system, exception, ignore_errors=ignore_errors)

    def _report_error_details(self, system, exception, ignore_errors=False):
        if isinstance(exception, GenerateError) and exception.original_exception is not None:
            self._report_error_details(system, exception.original_exception, ignore_errors=ignore_errors)
            return

        print('\nError report:')
        Printer.Instance().flush()
        print('\n\nTraceback Information:')
        traceback.print_tb(exception.__traceback__)
        print('\n\n>>>>>> END OF ERROR REPORT <<<<<<')
        if not ignore_errors:
            raise GenerateError('Generation failed.', original_exception=exception)

    def generate(self, ignore_errors=False):
        """Generate all systems in the dependency tree."""
        self._print_systems_forest()
        timestamp = datetime.datetime.now().strftime('%Y%m%d.%H%M')

        for node in self._walk_systems_forest():
            system = node.system
            command_list = node.command_list

            h1('Generate "{}"'.format(system))
            try:
                system_context = SystemContext(self._ctx, system=system,
                                               timestamp=timestamp)
                if os.path.isdir(system_context.storage_directory()):
                    verbose('Taking from storage.')
                else:
                    exe = Executor()
                    exe.run(system_context, system, command_list)

            except GenerateError as e:
                self._report_error(system, e, ignore_errors=ignore_errors)
            except Exception as e:
                self._report_error(system, e, ignore_errors=ignore_errors)
            else:
                success('Generation of "{}" complete.'.format(system))
