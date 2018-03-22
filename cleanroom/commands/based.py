"""Based command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.btrfs as btrfs

import re


class BasedCommand(cmd.Command):
    """The basedOn command."""

    def __init__(self):
        """Constructor."""
        super().__init__("based (on <SYSTEM_NAME>)",
                         "Use <SYSTEM_NAME> as a base for this system.\n\n"
                         "Note: This command needs to be the first in the\n"
                         "system definition file!")

    def validate_arguments(self, run_context, *args, **kwargs):
        """Validate the arguments."""
        base = None

        if len(args) != 2 or args[0] != 'on':
            raise ex.ParseError('"based" needs a "on" followed by a '
                                'system name.', run_context=run_context)
        elif len(args) == 2:
            base = args[1]

        assert(base)
        system_pattern = re.compile('^[A-Za-z][A-Za-z0-9_-]*$')
        if not system_pattern.match(base):
            raise ex.ParseError('"based" got invalid base system name "{}".'
                                .format(base), run_context=run_context)
        return base

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        base_system = args[1]

        self._restore_base(run_context, base_system)
        self._update_base_context(run_context, base_system)

        run_context.run_hooks('_setup')

    def _restore_base(self, run_context, base_system):
        btrfs.delete_subvolume(run_context,
                               run_context.current_system_directory())
        btrfs.create_snapshot(run_context,
                              run_context.storage_directory(base_system),
                              run_context.current_system_directory(),
                              read_only=False)

    def _update_base_context(self, run_context, base_system):
        run_context.unpickle_base_context(base_system)
        run_context.set_substitution('BASE_SYSTEM', base_system, local=True)

        run_context.base_system = base_system
