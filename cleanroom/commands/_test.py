"""_test command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.command as cmd
import cleanroom.helper.generic.run as run

import os
import os.path


class _TestCommand(cmd.Command):
    """The _test Command."""

    def __init__(self):
        """Constructor."""
        super().__init__("_test",
                         "Implicitly run after hooks on export/teardown.")

    def __call__(self, file_name, line_number, run_context, *args, **kwargs):
        """Execute command."""
        run_context.ctx.printer.h2('Running tests for system "{}"'
                                   .format(run_context.system),
                                   verbosity=2)
        env = self._environment(run_context)

        for test in self._find_tests(run_context):
            run_context.ctx.printer.debug('Running test {}...'.format(test))
            test_result \
                = run_context.run(test, env=env, outside=True, exit_code=None,
                                  work_directory=run_context.fs_directory())
            if test_result.returncode == 0:
                run_context.ctx.printer.success('Test "{}"'.format(test),
                                                verbosity=3)
            else:
                run.report_completed_process(run_context.ctx.printer.print,
                                             test_result)
                run_context.ctx.printer.fail('Test "{}"'.format(test))

    def _environment(self, run_context):
        """Generate environment for the system tests."""
        return {'PATH': '/usr/bin', **run_context.substitutions}

    def _find_tests(self, run_context):
        """Find tests to run."""
        test_directory = os.path.join(run_context.ctx.systems_directory(),
                                      'tests')
        run_context.ctx.printer.verbose('Searching for tests in "{}".'
                                        .format(test_directory))
        for f in sorted(os.listdir(test_directory)):
            test = os.path.join(test_directory, f)
            if not os.path.isfile(test):
                run_context.ctx.printer.trace('"{}": Not a file, skipping.'
                                              .format(test))
                continue
            if not os.access(test, os.X_OK):
                run_context.ctx.printer.trace('"{}": Not executable, skipping.'
                                              .format(test))
                continue

            run_context.ctx.printer.info('Found test: "{}"'.format(test))
            yield test
