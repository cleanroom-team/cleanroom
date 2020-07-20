# -*- coding: utf-8 -*-
"""_teardown command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.systemcontext import SystemContext
from cleanroom.location import Location
from cleanroom.printer import debug

import typing


class TeardownCommand(Command):
    """The _teardown Command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_teardown",
            help_string="Implicitly run after any other command of a " "system is run.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        self._run_hooks(system_context, "_teardown")
        self._run_hooks(system_context, "testing")

        system_context.pickle()

        self._execute(location, system_context, "_store")

        debug(
            'Cleaning up everything in "{}".'.format(system_context.scratch_directory)
        )
        self._service("btrfs_helper").delete_subvolume_recursive(
            system_context.scratch_directory
        )
