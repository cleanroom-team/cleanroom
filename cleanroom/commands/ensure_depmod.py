# -*- coding: utf-8 -*-
"""ensure_depmod command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class EnsureDepmodCommand(Command):
    """The ensure_depmod command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "ensure_depmod",
            help_string="Ensure that depmod is run for all kernels.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        location.set_description("Run ldconfig")
        self._add_hook(
            location, system_context, "export", "_depmod_all",
        )
