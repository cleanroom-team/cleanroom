# -*- coding: utf-8 -*-
"""The class that runs a list of print_commands on a system.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .commandmanager import CommandManager
from .execobject import ExecObject
from .systemcontext import SystemContext

import typing


class Executor:
    """Run a list of ExecObjects on a system."""

    def __init__(self, *,
                 scratch_directory: str,
                 systems_definition_directory: str,
                 command_manager: CommandManager,
                 timestamp: str) \
            -> None:
        assert scratch_directory
        assert systems_definition_directory

        self._scratch_directory = scratch_directory
        self._systems_definition_directory = systems_definition_directory
        self._command_manager = command_manager
        self._timestamp = timestamp

    def run(self, system_name: str, exec_obj_list: typing.List[ExecObject]) -> None:
        """Run the command_list for the system the executor was set up for."""
        with SystemContext(scratch_directory=self._scratch_directory,
                           systems_definition_directory=self._systems_definition_directory,
                           system_name=system_name,
                           timestamp=self._timestamp) as system_context:
            for exec_obj in exec_obj_list:
                command = self._command_manager.command(exec_obj.command)
                assert command
                command.execute_func(exec_obj.location, system_context,
                                     exec_obj.args, exec_obj.kwargs)



