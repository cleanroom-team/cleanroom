# -*- coding: utf-8 -*-
"""_test command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.command import Command
from cleanroom.helper.run import run, report_completed_process
from cleanroom.location import Location
from cleanroom.printer import debug, fail, h2, info, msg, success, trace
from cleanroom.systemcontext import SystemContext

import os
import os.path
import typing


def _environment(system_context: SystemContext) -> typing.Mapping[str, str]:
    """Generate environment for the system tests."""
    result = {k: str(v) for k, v in system_context.substitutions.items()}
    result["PATH"] = "/usr/bin"
    return result


def _find_tests(system_context: SystemContext) -> typing.Generator[str, None, None]:
    """Find tests to run."""
    tests_directory = system_context.system_tests_directory
    debug('Searching for tests in "{}".'.format(tests_directory))

    for f in sorted(os.listdir(tests_directory)):
        test = os.path.join(tests_directory, f)
        if not os.path.isfile(test):
            trace('"{}": Not a file, skipping.'.format(test))
            continue
        if not os.access(test, os.X_OK):
            trace('"{}": Not executable, skipping.'.format(test))
            continue

        info('Found test: "{}"'.format(test))
        yield test


class TestCommand(Command):
    """The _test Command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_test",
            help_string="Implicitly run to test images.\n\n"
            "Note: Will run all executable files in the "
            '"test" subdirectory of the systems directory and '
            "will pass the system name as first argument.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        h2(
            'Running tests for system "{}"'.format(system_context.system_name),
            verbosity=2,
        )
        env = _environment(system_context)

        for test in _find_tests(system_context):
            debug("Running test {}...".format(test))
            test_result = run(
                test,
                system_context.system_name,
                env=env,
                returncode=None,
                work_directory=system_context.fs_directory,
            )
            if test_result.returncode == 0:
                success('Test "{}"'.format(test), verbosity=3)
            else:
                report_completed_process(msg, test_result)
                fail('Test "{}"'.format(test))
