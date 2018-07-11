# -*- coding: utf-8 -*-
"""set_machine_id command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command

from cleanroom.exceptions import ParseError

import re


class SetMachineIdCommand(Command):
    """The set_machine_id command."""

    def __init__(self):
        """Constructor."""
        super().__init__('set_machine_id', syntax='<ID>',
                         help='Set the machine id of the system.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_arguments_exact(location, 1,
                                       '"{}" needs the machine id.',
                                       *args, **kwargs)

        id = args[0]
        assert(id)
        id_pattern = re.compile('^[A-Fa-f0-9]{32}$')
        if not id_pattern.match(id):
            raise ParseError('"{}" is not a valid machine-id.'.format(id),
                             location=location)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        if system_context.has_substitution('MACHINE_ID'):
            raise ex.GenerateError('Machine-id was already set.',
                                   location=location)

        id = args[0]
        system_context.set_substitution('MACHINE_ID', id)
        id += '\n'
        system_context.execute(location.next_line(), 'create', '/etc/machine-id', id)
