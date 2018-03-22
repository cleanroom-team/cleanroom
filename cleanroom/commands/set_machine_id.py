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

    def validate_arguments(self, run_context, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 1:
            raise ex.ParseError('set_machine_id needs the machine id.',
                                run_context=run_context)

        id = args[0]
        assert(id)
        id_pattern = re.compile('^[A-Fa-f0-9]{32}$')
        if not id_pattern.match(id):
            raise ex.ParseError('"{}" is not a valid machine-id.'.format(id),
                                run_context=run_context)
        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        if run_context.has_substitution('MACHINE_ID'):
            raise ex.GenerateError('Machine-id was already set.',
                                   run_context=run_context)

        id = args[0]
        run_context.set_substitution('MACHINE_ID', id)
        id += '\n'
        run_context.execute('create', '/etc/machine-id', id)
