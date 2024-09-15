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


class Generator:
    """Drives the generation of systems."""

    def __init__(self, systems_manager: SystemsManager) -> None:
        """Constructor."""
        self._systems_manager = systems_manager

    def _report_error(
        self, system: str, exception: Exception, ignore_errors: bool = False
    ) -> None:
        if isinstance(exception, AssertionError):
            fail(f'Generation of "{system}" asserted.', force_exit=False)
        else:
            fail(
                f'Generation of "{system}" failed: {str(exception)}',
                force_exit=False,
            )

        self._report_error_details(system, exception, ignore_errors=ignore_errors)

    def _report_error_details(
        self, system: str, exception: Exception, ignore_errors: bool = False
    ) -> None:
        if (
            isinstance(exception, CleanRoomError)
            and exception.original_exception is not None
        ):
            self._report_error_details(
                system, exception.original_exception, ignore_errors=ignore_errors
            )
            return

        print("\nError report:")
        Printer.instance().flush()
        print("\n\nTraceback Information:")
        traceback.print_tb(exception.__traceback__)
        print("\n\n>>>>>> END OF ERROR REPORT <<<<<<")
        if not ignore_errors:
            raise GenerateError("Generation failed.", original_exception=exception)

    def generate_systems(
        self,
        *,
        work_directory: WorkDir,
        command_manager: CommandManager,
        repository_base_directory: str = "",
        ignore_errors: bool = False,
    ) -> None:
        """Generate all systems in the dependency tree."""

        exe = Executor(
            scratch_directory=work_directory.scratch_directory,
            systems_definition_directory=self._systems_manager.systems_definition_directory,
            command_manager=command_manager,
            repository_base_directory=repository_base_directory,
            timestamp=datetime.datetime.now().strftime("%Y%m%d.%H%M"),
        )

        failed_systems = 0
        total_systems = 0

        for (
            system_name,
            target_distribution,
            base_system_name,
            exec_obj_list,
            _,
        ) in self._systems_manager.walk_systems_forest():
            total_systems += 1

            h1(f'Generate "{system_name}" ({target_distribution})')
            try:
                if os.path.isdir(
                    os.path.join(work_directory.storage_directory, system_name)
                ):
                    verbose("Already in storage, skipping.")
                else:
                    work_directory.clear_scratch_directory()

                    exe.run(
                        system_name,
                        base_system_name,
                        exec_obj_list,
                        storage_directory=work_directory.storage_directory,
                    )
            except Exception as e:
                self._report_error(system_name, e, ignore_errors=ignore_errors)
                failed_systems += 1

        if failed_systems == 0:
            success("All systems generated successfully.")
        else:
            fail(
                f"{failed_systems} of {total_systems} systems failed during generation phase."
            )
