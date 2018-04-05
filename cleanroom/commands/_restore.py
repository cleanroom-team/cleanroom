# -*- coding: utf-8 -*-
"""_restore command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.helper.generic.btrfs as btrfs
import cleanroom.printer as printer
import cleanroom.systemcontext as systemcontext


class RestoreCommand(cmd.Command):
    """The _restore command."""

    def __init__(self):
        """Constructor."""
        super().__init__('_restore', syntax='<STATIC> [pretty=<PRETTY>]',
                         help='Set the hostname of the system.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_arguments_exact(location, 1,
                                       '"{}" needs a base system to restore.',
                                       *args, **kwargs)
        return None

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        base_system = args[0]
        printer.debug('Restoring state from "{}".'.format(base_system))
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
