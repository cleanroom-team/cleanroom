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
        super().__init__('set_default_target <TARGET>',
                         'Set the systemd target to boot into.')

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 1:
            raise ex.ParseError(file_name, line_number,
                                'set_default_target needs a target name.')

        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        target = args[0]
        systemd_directory = '/usr/lib/systemd/system/'
        target_path = systemd_directory + args[0]

        if not file.isfile(run_context, target_path):
            raise ex.GenerateError('Target "{}" does not exist or is no file. '
                                   'Can not use as default target.'
                                   .format(target))

        default = 'default.target'
        default_path = systemd_directory + 'default.target'

        file.remove(run_context, default_path, force=True)
        file.symlink(run_context, target, default,
                     base_directory=systemd_directory)
