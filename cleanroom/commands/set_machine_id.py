# -*- coding: utf-8 -*-
"""set_machine_id command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.exceptions import GenerateError, ParseError
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import re
import typing


class SetMachineIdCommand(Command):
    """The set_machine_id command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "set_machine_id",
            syntax="<ID>",
            help_string="Set the machine id of the system.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_arguments_exact(
            location, 1, '"{}" needs the machine id.', *args, **kwargs
        )

        machine_id = args[0]
        assert machine_id

        id_pattern = re.compile("^[A-Fa-f0-9]{32}$")
        if not id_pattern.match(machine_id):
            raise ParseError(
                f'"{machine_id}" is not a valid machine-id.', location=location
            )

    def register_substitutions(self) -> typing.List[typing.Tuple[str, str, str]]:
        return [
            (
                "MACHINE_ID",
                "",
                "The machine id for the system. Only valid after set_machine_id was called",
            ),
        ]

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        old_machine_id = system_context.substitution("MACHINE_ID", "")
        if old_machine_id:
            raise GenerateError(
                f'Machine-id was already set to "{old_machine_id}".', location=location,
            )

        machine_id = args[0]
        system_context.set_substitution("MACHINE_ID", machine_id)
        machine_id += "\n"
        self._execute(
            location.next_line(),
            system_context,
            "create",
            "/etc/machine-id",
            machine_id,
        )
