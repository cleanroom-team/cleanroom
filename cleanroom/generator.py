# -*- coding: utf-8 -*-
"""The class that drives the system generation.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from __future__ import annotations

from .commandmanager import CommandManager
from .exceptions import CleanRoomError, GenerateError
from .executor import Executor
from .printer import fail, h1, success, verbose, Printer
from .systemsmanager import SystemsManager
from .workdir import WorkDir

import datetime
import os
import os.path
import traceback
import typing


class Generator:
    """Drives the generation of systems."""

    def __init__(self, systems_manager: SystemsManager) -> None:
        """Constructor."""
        self._systems_manager = systems_manager

    def _report_error(self, system: str, exception: Exception,
                      ignore_errors: bool = False) -> None:
        if isinstance(exception, AssertionError):
            fail('Generation of "{}" asserted.'.format(system), force_exit=False)
        else:
            fail('Generation of "{}" failed: {}'.format(system, str(exception)),
                 force_exit=False)

        self._report_error_details(system, exception, ignore_errors=ignore_errors)

    def _report_error_details(self, system: str, exception: Exception,
                              ignore_errors: bool = False) -> None:
        if isinstance(exception, CleanRoomError) and exception.original_exception is not None:
            self._report_error_details(system, exception.original_exception, ignore_errors=ignore_errors)
            return

        print('\nError report:')
        Printer.instance().flush()
        print('\n\nTraceback Information:')
        traceback.print_tb(exception.__traceback__)
        print('\n\n>>>>>> END OF ERROR REPORT <<<<<<')
        if not ignore_errors:
            raise GenerateError('Generation failed.', original_exception=exception)

    def generate_systems(self, *, work_directory: WorkDir,
                         command_manager: CommandManager,
                         ignore_errors: bool = False) -> None:
        """Generate all systems in the dependency tree."""

        exe = Executor(scratch_directory=work_directory.scratch_directory,
                       systems_definition_directory=self._systems_manager.systems_definition_directory,
                       command_manager=command_manager,
                       timestamp=datetime.datetime.now().strftime('%Y%m%d.%H%M'))

        for (system_name, exec_obj_list, _) in self._systems_manager.walk_systems_forest():
            h1('Generate "{}"'.format(system_name))
            try:
                if os.path.isdir(work_directory.storage_directory):
                    verbose('Already in storage, skipping.')
                else:
                    exe.run(system_name, exec_obj_list)
            except Exception as e:
                self._report_error(system_name, e, ignore_errors=ignore_errors)
            else:
                success('Generation of "{}" complete.'.format(system_name))
