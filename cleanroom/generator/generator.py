# -*- coding: utf-8 -*-
"""The class that drives the system generation.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from __future__ import annotations

from .commandmanager import CommandManager
from .context import Binaries, Context
from .execobject import ExecObject
from .executor import Executor
from .parser import Parser
from .systemcontext import SystemContext

from ..exceptions import CleanRoomError, GenerateError, SystemNotFoundError
from ..printer import (debug, fail, h1, h2, success, trace, verbose, Printer,)

import datetime
import os
import os.path
import traceback
import typing


class DependencyNode:
    """Node of the dependency tree of all systems."""

    def __init__(self, system: str, parent: typing.Optional[DependencyNode],
                 exec_obj_list: typing.List[ExecObject]) -> None:
        """Constructor."""
        # Tree:
        self.parent = parent
        self.children: typing.List[DependencyNode] = []

        # Payload:
        self.system = system
        self.exec_obj_list = exec_obj_list

        assert(system)
        assert(len(exec_obj_list) >= 2)  # At least _setup and _teardown!

    def find(self, system: str) -> typing.Optional[DependencyNode]:
        """Find a system in the dependency tree."""
        if self.system == system:
            return self

        for cn in self.children:
            if cn.find(system):
                return cn

        return None

    def walk(self) -> typing.Generator[DependencyNode, None, None]:
        """Walk the nodes in pre-order."""
        yield(self)

        for child in self.children:
            for node in child.walk():
                yield node

    def depth(self) -> int:
        """Calculate the distance from the root node."""
        if self.parent:
            return self.parent.depth() + 1
        return 0


class Generator:
    """Drives the generation of systems."""

    def __init__(self, ctx: Context) -> None:
        """Constructor."""
        self._ctx = ctx
        self._systems_forest: typing.List[DependencyNode] = []

        # Find commands:
        self._command_manager = CommandManager()
        systems_commands_dir = ctx.systems_commands_directory()
        assert systems_commands_dir
        commands_dir = ctx.commands_directory()
        assert commands_dir
        self._command_manager.find_commands(systems_commands_dir, commands_dir)

    def _binary(self, selector: Binaries):
        """Get the full path to a binary."""
        return self._ctx.binary(selector)

    def add_system(self, system: typing.Optional[str]) -> typing.Optional[DependencyNode]:
        """Add a system to the dependency tree."""
        if not system:
            return None

        debug('Adding system "{}".'.format(system))

        node = self._find(system)
        if node:
            trace('Found system "{}" in system_forest.'.format(system))
            return node

        system_file = self._find_system_definition_file(system)
        (base_system, exec_obj_list) \
            = self._parse_system_definition_file(system_file)

        trace('"{}" depends on "{}"'.format(system, base_system))
        parent_node = self.add_system(base_system)
        node = DependencyNode(system, parent_node, exec_obj_list)

        if parent_node:
            parent_node.children.append(node)
        else:
            self._systems_forest.append(node)

        return node

    def _parse_system_definition_file(self, system_file: str) \
            -> typing.Tuple[typing.Optional[str], typing.List[ExecObject]]:
        trace('Parsing "{}".'.format(system_file))
        system_parser = Parser(self._command_manager)
        exec_obj_list: typing.List[ExecObject] = []
        for exec_obj in system_parser.parse(system_file):
            exec_obj_list.append(exec_obj)

        base_system = None
        for exec_object in exec_obj_list:
            if exec_object.dependency():
                base_system = exec_object.dependency()
                break

        return (base_system, exec_obj_list)

    def _find_system_definition_file(self, system: str) -> str:
        """Make sure a system definition file can be found."""
        systems_dir = self._ctx.systems_directory()
        assert systems_dir
        system_file = os.path.join(systems_dir, system + '.def')
        if not os.path.exists(system_file):
            raise SystemNotFoundError('Could not find systems file for {}, checked in {}.'
                                      .format(system, system_file))

        return system_file

    def _find(self, system: str) -> typing.Optional[DependencyNode]:
        """Find a system in the dependency tree."""
        for root_node in self._systems_forest:
            node = root_node.find(system)
            if node:
                return node

        return None

    def _print_systems_forest(self) -> None:
        """Print the systems forest."""
        base_indent = "  "
        debug('Systems forest ({} trees):'.format(len(self._systems_forest)))
        for node in self._walk_systems_forest():
            debug('  {}{} ({} children)'.format(base_indent * node.depth(),
                                                node.system, len(node.children)))

    def _walk_systems_forest(self) -> typing.Generator[DependencyNode, None, None]:
        for root_node in self._systems_forest:
            for node in root_node.walk():
                yield node

    def prepare(self) -> None:
        """Prepare for generation."""
        h2('Preparing for system generation')
        storage_dir = self._ctx.storage_directory()
        assert storage_dir
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

    def _report_error(self, system: str, exception: Exception,
                      ignore_errors: bool=False) -> None:
        if isinstance(exception, AssertionError):
            fail('Generation of "{}" asserted.'.format(system), force_exit=False)
        else:
            fail('Generation of "{}" failed: {}'.format(system, str(exception)),
                 force_exit=False)

        self._report_error_details(system, exception, ignore_errors=ignore_errors)

    def _report_error_details(self, system: str, exception: Exception,
                              ignore_errors: bool=False) -> None:
        if isinstance(exception, CleanRoomError) and exception.original_exception is not None:
            self._report_error_details(system, exception.original_exception, ignore_errors=ignore_errors)
            return

        print('\nError report:')
        Printer.Instance().flush()
        print('\n\nTraceback Information:')
        traceback.print_tb(exception.__traceback__)
        print('\n\n>>>>>> END OF ERROR REPORT <<<<<<')
        if not ignore_errors:
            raise GenerateError('Generation failed.', original_exception=exception)

    def generate(self, ignore_errors: bool=False) -> None:
        """Generate all systems in the dependency tree."""
        self._print_systems_forest()
        timestamp = datetime.datetime.now().strftime('%Y%m%d.%H%M')

        for node in self._walk_systems_forest():
            system = node.system
            exec_obj_list = node.exec_obj_list

            h1('Generate "{}"'.format(system))
            try:
                system_context = SystemContext(self._ctx, self._command_manager,
                                               system=system,
                                               timestamp=timestamp)
                if os.path.isdir(system_context.storage_directory()):
                    verbose('Taking from storage.')
                else:
                    exe = Executor()
                    exe.run(system_context, system, exec_obj_list)

            except Exception as e:
                self._report_error(system, e, ignore_errors=ignore_errors)
            else:
                success('Generation of "{}" complete.'.format(system))
