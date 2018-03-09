"""set_machine_id command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file

import re


class SetMachineIdCommand(cmd.Command):
    """The set_machine_id command."""

    def __init__(self):
        """Constructor."""
        super().__init__('set_machine_id <ID>]',
                         'Set the machine id of the system.')

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 1:
            raise ex.ParseError('set_machine_id needs the machine id.',
                                file_name=file_name, line_number=line_number)

        id = args[0]
        assert(id)
        id_pattern = re.compile('^[A-Fa-f0-9]{32}$')
        if not id_pattern.match(id):
            raise ex.ParseError('"{}" is not a valid machine-id.'.format(id),
                                file_name=file_name, line_number=line_number)

        return None

    def __call__(self, file_name, line_number, run_context, *args, **kwargs):
        """Execute command."""
        id = args[0] + '\n'

        file.create_file(run_context, '/etc/machine-id', id.encode('utf-8'))
