# -*- coding: utf-8 -*-
"""The class that drives the system generation.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from __future__ import annotations

from .commandmanager import CommandManager
from .exceptions import ParseError, SystemNotFoundError
from .execobject import ExecObject
from .location import Location
from .parser import Parser
from .printer import debug, info, trace, verbose

import os
import os.path
import typing


class _DependencyNode(object):
    """Node of the dependency tree of all systems."""

    def __init__(
        self,
        system: str,
        target_distribution: str,
        parent: typing.Optional[_DependencyNode],
        exec_obj_list: typing.List[ExecObject],
    ) -> None:
        """Constructor."""
        assert system
        assert len(exec_obj_list) >= 1  # At least _teardown

        # Tree:
        self.parent = parent
        self.children: typing.List[_DependencyNode] = []

        # Payload:
        self.system = system
        self.target_distribution = target_distribution
        self.exec_obj_list = exec_obj_list

    def find(self, system: str) -> typing.Optional[_DependencyNode]:
        """Find a system in the dependency tree."""
        if self.system == system:
            return self

        for cn in self.children:
            result = cn.find(system)
            if result:
                return result

        return None

    def walk(self) -> typing.Generator[_DependencyNode, None, None]:
        """Walk the nodes in pre-order."""
        yield (self)

        for child in self.children:
            for node in child.walk():
                yield node

    @property
    def depth(self) -> int:
        """Calculate the distance from the root node."""
        if self.parent:
            return self.parent.depth + 1
        return 0

    def append_child(self, child: _DependencyNode):
        if self.target_distribution and child.target_distribution:
            if self.target_distribution != child.target_distribution:
                raise ParseError(
                    f"Target distribution mismatch between {self.system}(== {self.target_distribution}) "
                    + f"and {child.system}(== {child.target_distribution})"
                )
        else:
            if self.target_distribution:
                child.target_distribution = self.target_distribution
            elif child.target_distribution:
                self.target_distribution = child.target_distribution
                for c in self.children:
                    assert not c.target_distribution
                    c.target_distribution = self.target_distribution

        self.children.append(child)


class SystemsManager(object):
    """Drives the generation of systems."""

    def __init__(
        self,
        command_manager: CommandManager,
        systems_definition_directory: str,
        *systems: str,
    ) -> None:
        """Constructor."""
        self._command_manager = command_manager
        assert systems_definition_directory
        self._systems_definition_directory = systems_definition_directory
        self._systems_forest: typing.List[_DependencyNode] = []

        systems_str = ", ".join(systems)
        verbose(f"Requested systems: {systems_str}.")
        for system in systems:
            if system.endswith(".def"):
                system = system[:-4]
            self._add_system(system)

        self._print_systems_forest()

    def walk_systems_forest(
        self,
    ) -> typing.Generator[
        typing.Tuple[str, str, typing.Optional[str], typing.List[ExecObject], int],
        None,
        None,
    ]:
        for root_node in self._systems_forest:
            for node in root_node.walk():
                base_system = node.parent.system if node.parent else None
                debug(
                    f"yielding ({node.system}, {node.target_distribution}, {base_system}, <COMMANDS>)"
                )
                yield (
                    node.system,
                    node.target_distribution,
                    base_system,
                    node.exec_obj_list,
                    node.depth,
                )

    @property
    def systems_definition_directory(self) -> str:
        return self._systems_definition_directory

    def _print_systems_forest(self) -> None:
        """Print the systems forest."""
        base_indent = "  "
        debug(f"Systems forest ({len(self._systems_forest)} trees):")
        for (
            system_name,
            target_distribution,
            _,
            exec_obj_list,
            depth,
        ) in self.walk_systems_forest():
            debug(
                f"  {base_indent * depth}{system_name} ({len(exec_obj_list)} commands, {target_distribution})"
            )

    def _add_system(self, system_name: str) -> typing.Optional[_DependencyNode]:
        """Add a system to the dependency tree."""
        if system_name == "scratch":
            return None

        info(f'Adding system "{system_name}".')

        node = self._find(system_name)
        if node:
            trace(f'Found system "{system_name}" in system_forest (skipping addition).')
            return node

        system_file = self._find_system_definition_file(system_name)
        (
            base_system_name,
            target_distribution,
            exec_obj_list,
        ) = self._parse_system_definition_file(system_file)

        if not exec_obj_list:
            return None

        location = Location(
            file_name="<built-in>", line_number=1, description="System setup"
        )
        exec_obj_list.append(ExecObject(location.next_line(), "_teardown", (), {}))

        debug(f'"{system_name}" depends on "{base_system_name}"')

        parent_node = self._add_system(base_system_name) if base_system_name else None
        assert not base_system_name or (
            parent_node and parent_node.system == base_system_name
        )

        node = _DependencyNode(
            system_name, target_distribution, parent_node, exec_obj_list
        )

        if parent_node:
            parent_node.append_child(node)
        else:
            self._systems_forest.append(node)

        return node

    def _parse_system_definition_file(
        self, system_file: str
    ) -> typing.Tuple[str, str, typing.List[ExecObject]]:
        debug(f'Parsing "{system_file}".')
        system_parser = Parser(self._command_manager)
        (base_system_name, target_distribution, exec_obj_list) = system_parser.parse(
            system_file
        )
        if not base_system_name:
            raise ParseError(f'No base system was provided in "{system_file}".')
        if base_system_name == "scratch":
            base_system_name = ""

        return base_system_name, target_distribution, exec_obj_list

    def _find_system_definition_file(self, system: str) -> str:
        """Make sure a system definition file can be found."""
        system_file = os.path.join(self._systems_definition_directory, system + ".def")
        if not os.path.exists(system_file):
            raise SystemNotFoundError(
                f"Could not find systems file for {system}, checked in {system_file}."
            )

        return system_file

    def _find(self, system: str) -> typing.Optional[_DependencyNode]:
        """Find a system in the dependency tree."""
        for root_node in self._systems_forest:
            node = root_node.find(system)
            if node:
                return node

        return None
