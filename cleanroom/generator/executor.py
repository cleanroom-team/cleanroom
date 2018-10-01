# -*- coding: utf-8 -*-
"""The class that runs a list of commands on a system.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .execobject import ExecObject
from .systemcontext import SystemContext

from ..location import Location
from ..printer import fail, h2, trace, success
from ..exceptions import GenerateError

import os
import os.path
import typing


class Executor:
    """Run a list of commands on a system."""

    def run(self, system_context: SystemContext, system: str,
            exec_obj_list: typing.List[ExecObject]) -> None:
        """Run the command_list for the system the executor was set up for."""
        h2('Running commands for system "{}".'.format(system), verbosity=2)
        if not self._setup_for_execution(system_context):
            return  # Return early when system already set up

        trace('Running commands for system "{}".'
              .format(system_context.system))

        self._run_commands(system_context, exec_obj_list)

    def _setup_for_execution(self, system_context: SystemContext) -> bool:
        if self._system_already_built(system_context):
            return False

        """Set up execution context."""
        trace('Setup for execution of commands of "{}".'
              .format(system_context.system))

        return True

    def _system_already_built(self, system_context: SystemContext) -> bool:
        """Check whether system has been built already."""
        return os.path.isdir(system_context.storage_directory())

    def _execute(self, location: Location, system_context: SystemContext,
                 exec_object: ExecObject) -> None:
        """Execute the command."""
        trace('Executing "{}".'.format(exec_object))

        try:
            system_context.execute(
                exec_object.location(), exec_object.command(),
                *exec_object.arguments(),
                expected_dependency=exec_object.dependency(),
                **exec_object.kwargs())
        except Exception as e:
            raise GenerateError('Failed to execute {} for system {}.'
                                .format(exec_object, system_context.system),
                                location=location, original_exception=e)
        else:
            success('{}: ok.'.format(exec_object), verbosity=1)

    def _run_commands(self, system_context: SystemContext,
                      exec_obj_list: typing.List[ExecObject]) -> None:
        """Run commands."""
        for eo in exec_obj_list:
            os.chdir(system_context.systems_directory())
            self._execute(eo._location, system_context, eo)
