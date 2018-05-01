# -*- coding: utf-8 -*-
"""_test command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.command as cmd
import cleanroom.helper.generic.run as run
import cleanroom.printer as printer

import os
import os.path


class _TestCommand(cmd.Command):
    """The _test Command."""

    def __init__(self):
        """Constructor."""
        super().__init__('_test',
                         help='Implicitly run to test images.\n\n'
                         'Note: Will run all executable files in the '
                         '"test" subdirectory of the systems directory and '
                         'will pass the system name as first argument.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        printer.h2('Running tests for system "{}"'
                   .format(system_context.system),
                   verbosity=2)
        env = self._environment(system_context)

        for test in self._find_tests(system_context):
            printer.debug('Running test {}...'.format(test))
            test_result = system_context.run(
                test, system_context.system,
                env=env, outside=True, exit_code=None,
                work_directory=system_context.fs_directory())
            if test_result.returncode == 0:
                printer.success('Test "{}"'.format(test), verbosity=3)
            else:
                run.report_completed_process(printer.msg, test_result)
                printer.fail('Test "{}"'.format(test))

    def _environment(self, system_context):
        """Generate environment for the system tests."""
        result = {k: str(v) for k, v in system_context.substitutions.items()}
        result['PATH'] = '/usr/bin'
        return result

    def _find_tests(self, system_context):
        """Find tests to run."""
        test_directory = os.path.join(system_context.ctx.systems_directory(),
                                      'tests')
        printer.verbose('Searching for tests in "{}".'.format(test_directory))
        for f in sorted(os.listdir(test_directory)):
            test = os.path.join(test_directory, f)
            if not os.path.isfile(test):
                printer.trace('"{}": Not a file, skipping.'.format(test))
                continue
            if not os.access(test, os.X_OK):
                printer.trace('"{}": Not executable, skipping.'.format(test))
                continue

            printer.info('Found test: "{}"'.format(test))
            yield test
