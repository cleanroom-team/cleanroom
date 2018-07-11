# -*- coding: utf-8 -*-
"""The class that runs a list of commands on a system.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from ..printer import (fail, h2, trace, success,)
from ..exceptions import GenerateError

import os
import os.path


class Executor:
    """Run a list of commands on a system."""

    def run(self, system_context, system, command_list):
        """Run the command_list for the system the executor was set up for."""
        h2('Running commands for system "{}".'.format(system), verbosity=2)
        if not self._setup_for_execution(system_context):
            return  # Return early when system already set up

        trace('Running commands for system "{}".'
              .format(system_context.system))

        self._run_commands(command_list, system_context)

    def _setup_for_execution(self, system_context):
        if self._system_already_built(system_context):
            return False

        """Set up execution context."""
        trace('Setup for execution of commands of "{}".'
              .format(system_context.system))

        return True

    def _system_already_built(self, system_context):
        """Check whether system has been built already."""
        return os.path.isdir(system_context.storage_directory())

    def _execute(self, location, system_context, exec_object):
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

    def _run_commands(self, command_list, system_context):
        """Run commands."""
        for command in command_list:
            os.chdir(system_context.ctx.systems_directory())
            self._execute(command._location, system_context, command)
