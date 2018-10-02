# -*- coding: utf-8 -*-
"""Parse system definition files.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from ..location import Location

import typing


class ExecObject:
    """Describe command in system definition file.

    Describe the command to execute later during generation phase.
    """

    def __init__(self, location: Location, dependency: typing.Optional[str],
                 command: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Constructor."""
        assert command

        self._location = location
        self._dependency = dependency
        self._args = args
        self._command = command
        self._kwargs = kwargs

        if not self._location.description:
            self._location.description = self.command()

    def command(self) -> str:
        """Name of the command to execute."""
        return self._command

    def arguments(self) -> typing.Tuple[typing.Any, ...]:
        """Arguments passed to command()."""
        return self._args

    def kwargs(self) -> typing.Dict[str, typing.Any]:
        """Keyword arguments to command()."""
        return self._kwargs

    def set_dependency(self, dependency: typing.Optional[str]) -> None:
        """Set dependency."""
        self._dependency = dependency

    def dependency(self) -> typing.Optional[str]:
        """Return dependency of the system (or None)."""
        return self._dependency

    def location(self) -> Location:
        """Return location."""
        return self._location

    def __str__(self) -> str:
        """Turn into string object."""
        return '{}: {},{}'.format(self._location, self._args, self._kwargs)
