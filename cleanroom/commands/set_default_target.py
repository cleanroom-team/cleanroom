# -*- coding: utf-8 -*-
"""set_default_target command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file


class SetDefaultTargetCommand(cmd.Command):
    """The set_default_target command."""

    def __init__(self):
        """Constructor."""
        super().__init__('set_default_target', syntax='<TARGET>',
                         help='Set the systemd target to boot into.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 1:
            raise ex.ParseError('set_default_target needs a target name.',
                                location=location)
        return None

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        target = args[0]
        systemd_directory = '/usr/lib/systemd/system/'
        target_path = systemd_directory + args[0]

        if not file.isfile(system_context, target_path):
            raise ex.GenerateError('Target "{}" does not exist or is no file. '
                                   'Can not use as default target.'
                                   .format(target))

        default = 'default.target'
        default_path = systemd_directory + 'default.target'

        system_context.execute(location, 'remove', default_path, force=True)
        system_context.execute(location, 'symlink', target, default,
                               base_directory=systemd_directory)

        system_context.set_substitution('DEFAULT_BOOT_TARGET', target)
