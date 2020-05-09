# -*- coding: utf-8 -*-
"""The class that runs a list of commands on a system.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .commandmanager import CommandManager
from .execobject import ExecObject
from .printer import success
from .systemcontext import SystemContext

import os
import typing


class Executor:
    """Run a list of ExecObjects on a system."""

    def __init__(
        self,
        *,
        scratch_directory: str,
        systems_definition_directory: str,
        command_manager: CommandManager,
        repository_base_directory: str,
        timestamp: str
    ) -> None:
        assert scratch_directory
        assert systems_definition_directory

        self._scratch_directory = scratch_directory
        self._systems_definition_directory = systems_definition_directory
        self._command_manager = command_manager
        self._timestamp = timestamp
        self._repository_base_directory = repository_base_directory

    def run(
        self,
        system_name: str,
        base_system_name: typing.Optional[str],
        exec_obj_list: typing.List[ExecObject],
        storage_directory: str,
    ) -> None:
        """Run the command_list for the system the executor was set up for."""
        with SystemContext(
            system_name=system_name,
            base_system_name=base_system_name or "",
            scratch_directory=self._scratch_directory,
            systems_definition_directory=self._systems_definition_directory,
            storage_directory=storage_directory,
            repository_base_directory=self._repository_base_directory,
            timestamp=self._timestamp,
        ) as system_context:
            for exec_obj in exec_obj_list:
                os.chdir(system_context.systems_definition_directory)
                command = self._command_manager.command(exec_obj.command)
                assert command
                command.execute_func(
                    exec_obj.location, system_context, *exec_obj.args, **exec_obj.kwargs
                )
        success("System {} created successfully.".format(system_name))
