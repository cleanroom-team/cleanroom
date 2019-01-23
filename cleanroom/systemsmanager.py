# -*- coding: utf-8 -*-
"""The class that drives the system generation.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from __future__ import annotations

from .commandmanager import CommandManager
from .exceptions import SystemNotFoundError
from .execobject import ExecObject
from .location import Location
from .parser import Parser
from .printer import debug, trace

import os
import os.path
import typing


class _DependencyNode(object):
    """Node of the dependency tree of all systems."""

    def __init__(self, system: str, parent: typing.Optional[_DependencyNode],
                 exec_obj_list: typing.List[ExecObject]) -> None:
        """Constructor."""
        assert system
        assert len(exec_obj_list) >= 2  # At least _setup and _teardown

        # Tree:
        self.parent = parent
        self.children: typing.List[_DependencyNode] = []

        # Payload:
        self.system = system
        self.exec_obj_list = exec_obj_list

    def find(self, system: str) -> typing.Optional[_DependencyNode]:
        """Find a system in the dependency tree."""
        if self.system == system:
            return self

        for cn in self.children:
            if cn.find(system):
                return cn

        return None

    def walk(self) -> typing.Generator[_DependencyNode, None, None]:
        """Walk the nodes in pre-order."""
        yield(self)

        for child in self.children:
            for node in child.walk():
                yield node

    @property
    def depth(self) -> int:
        """Calculate the distance from the root node."""
        if self.parent:
            return self.parent.depth + 1
        return 0


class SystemsManager(object):
    """Drives the generation of systems."""

    def __init__(self, command_manager: CommandManager,
                 systems_definition_directory: str, *systems: str) -> None:
        """Constructor."""
        self._command_manager = command_manager
        assert systems_definition_directory
        self._systems_definition_directory = systems_definition_directory
        self._systems_forest: typing.List[_DependencyNode] = []

        for system in systems:
            self._add_system(system)

        self._print_systems_forest()

    def walk_systems_forest(self) -> typing.Generator[typing.Tuple[str,
                                                                   typing.List[ExecObject], int],
                                                      None, None]:
        for root_node in self._systems_forest:
            for node in root_node.walk():
                yield node.system, node.exec_obj_list, node.depth

    @property
    def systems_definition_directory(self) -> str:
        return self._systems_definition_directory

    def _print_systems_forest(self) -> None:
        """Print the systems forest."""
        base_indent = "  "
        debug('Systems forest ({} trees):'.format(len(self._systems_forest)))
        for (system_name, exec_obj_list, depth) in self.walk_systems_forest():
            debug('  {}{} ({} commands)'.format(base_indent * depth,
                                                system_name, len(exec_obj_list)))

    def _add_system(self, system: typing.Optional[str]) -> typing.Optional[_DependencyNode]:
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

        location = Location(file_name='<built-in>', line_number=1,
                            description='System setup')
        exec_obj_list = [ExecObject(location, '_setup', [], {}),
                         *exec_obj_list,
                         ExecObject(location.next_line(), '_teardown', [], {})]

        trace('"{}" depends on "{}"'.format(system, base_system))
        parent_node = self._add_system(base_system)
        node = _DependencyNode(system, parent_node, exec_obj_list)

        if parent_node:
            parent_node.children.append(node)
        else:
            self._systems_forest.append(node)

        return node

    def _parse_system_definition_file(self, system_file: str) \
            -> typing.Tuple[str, typing.List[ExecObject]]:
        trace('Parsing "{}".'.format(system_file))
        system_parser = Parser(self._command_manager)
        parse_result = system_parser.parse(system_file)
        assert parse_result
        return parse_result

    def _find_system_definition_file(self, system: str) -> str:
        """Make sure a system definition file can be found."""
        system_file = os.path.join(self._systems_definition_directory,
                                   system + '.def')
        if not os.path.exists(system_file):
            raise SystemNotFoundError('Could not find systems file for {}, checked in {}.'
                                      .format(system, system_file))

        return system_file

    def _find(self, system: str) -> typing.Optional[_DependencyNode]:
        """Find a system in the dependency tree."""
        for root_node in self._systems_forest:
            node = root_node.find(system)
            if node:
                return node

        return None
