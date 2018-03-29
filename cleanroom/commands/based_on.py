# -*- coding: utf-8 -*-
"""based_on command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.btrfs as btrfs
import cleanroom.systemcontext as systemcontext

import re


class BasedOnCommand(cmd.Command):
    """The based_on command."""

    def __init__(self):
        """Constructor."""
        super().__init__('based_on', syntax='<SYSTEM_NAME>)',
                         help='Use <SYSTEM_NAME> as a base for this '
                         'system.\n\n'
                         'Note: This command needs to be the first in the '
                         'system definition file!')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        base = None

        self._validate_arguments_exact(location, 1,
                                       '"{}" needs a system name.', *args)
        base = args[0]
        assert(base)

        system_pattern = re.compile('^[A-Za-z][A-Za-z0-9_-]*$')
        if not system_pattern.match(base):
            raise ex.ParseError('"{}" got invalid base system name "{}".'
                                .format(self.name(), base), location=location)
        return base

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        base_system = args[0]
        base_context = systemcontext.SystemContext(system_context.ctx,
                                            system=base_system)


        self._restore_base(system_context, base_context)
        self._update_base_context(system_context, base_context)

        system_context.run_hooks('_setup')

    def _restore_base(self, system_context, base_context):
        btrfs.delete_subvolume(system_context,
                               system_context.ctx.current_system_directory())
        btrfs.create_snapshot(system_context,
                              base_context.storage_directory(),
                              system_context.ctx.current_system_directory(),
                              read_only=False)

    def _update_base_context(self, system_context, base_context):
        base_unpickle = base_context.unpickle()
        system_context.install_base_context(base_unpickle)
