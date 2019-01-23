# -*- coding: utf-8 -*-
"""set_machine_id command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.exceptions import GenerateError, ParseError
from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import re
import typing


class SetMachineIdCommand(Command):
    """The set_machine_id command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('set_machine_id', syntax='<ID>',
                         help_string='Set the machine id of the system.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_arguments_exact(location, 1, '"{}" needs the machine id.', *args, **kwargs)

        machine_id = args[0]
        assert machine_id

        id_pattern = re.compile('^[A-Fa-f0-9]{32}$')
        if not id_pattern.match(machine_id):
            raise ParseError('"{}" is not a valid machine-id.'.format(machine_id),
                             location=location)

        return None

    def __call__(self, location: Location, system_context: SystemContext, 
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        if system_context.has_substitution('MACHINE_ID'):
            raise GenerateError('Machine-id was already set.', location=location)

        machine_id = args[0]
        system_context.set_substitution('MACHINE_ID', machine_id)
        machine_id += '\n'
        system_context.execute(location.next_line(), 'create', '/etc/machine-id', machine_id)
