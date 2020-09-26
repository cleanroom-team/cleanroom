# -*- coding: utf-8 -*-
"""set_hostname command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.exceptions import GenerateError
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class SetHostnameCommand(Command):
    """The set_hostname command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "set_hostname",
            syntax="<STATIC> [pretty=<PRETTY>]",
            help_string="Set the hostname of the system.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs a static hostname.', *args)
        self._validate_kwargs(location, ("pretty",), **kwargs)

    def register_substitutions(self) -> typing.List[typing.Tuple[str, str, str]]:
        return [
            ("HOSTNAME", "", "The hostname to be set"),
            ("PRETTY_HOSTNAME", "", "The pretty hostname to set"),
        ]

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        static_hostname = args[0]
        pretty_hostname = kwargs.get("pretty", static_hostname)

        if system_context.substitution("HOSTNAME", ""):
            raise GenerateError("Hostname was already set.", location=location)

        system_context.set_substitution("HOSTNAME", static_hostname)
        system_context.set_substitution("PRETTY_HOSTNAME", pretty_hostname)

        self._execute(
            location, system_context, "create", "/etc/hostname", static_hostname
        )
        self._execute(
            location.next_line(),
            system_context,
            "sed",
            f'/^PRETTY_HOSTNAME=/ cPRETTY_HOSTNAME="{pretty_hostname}"',
            "/etc/machine.info",
        )
