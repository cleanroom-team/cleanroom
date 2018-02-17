"""Based command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.context as context
import cleanroom.exceptions as ex

import re
import shutil


class BasedCommand(cmd.Command):
    """The basedOn command."""

    def __init__(self):
        """Constructor."""
        super().__init__("based (on <SYSTEM_NAME>)",
                         "Use <SYSTEM_NAME> as a base for this system.\n\n"
                         "Note: This command needs to be the first in the\n"
                         "system definition file!")

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        base = None

        if len(args) != 2 or args[0] != 'on':
            print('>>>>', args, type(args))
            raise ex.ParseError('"based" needs a "on" followed by a '
                                'system name.',
                                file_name=file_name, line_number=line_number)
        elif len(args) == 2:
            base = args[1]

        assert(base)
        system_pattern = re.compile('^[A-Za-z][A-Za-z0-9_-]*$')
        if not system_pattern.match(base):
            raise ex.ParseError('"based" got invalid base system name "{}".'
                                .format(base),
                                file_name=file_name, line_number=line_number)

        return base

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        base_system = args[1]

        self._ostree_checkout(run_context, base_system)
        self._update_base_context(run_context, base_system)

    def _ostree_checkout(self, run_context, base_system):
        shutil.rmtree(run_context.system_directory())

        ostree = run_context.ctx.binary(context.Binaries.OSTREE)
        repo = run_context.ctx.work_repository_directory()

        run_context.run(ostree, '--repo={}'.format(repo),
                        'checkout', base_system,
                        run_context.system_directory(),
                        outside=True,
                        work_directory=repo)

    def _update_base_context(self, run_context, base_system):
        run_context.unpickle_base_context(base_system)
        run_context.set_substitution('BASE_SYSTEM', base_system, local=True)

        run_context.base_system = base_system
