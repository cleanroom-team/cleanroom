# -*- coding: utf-8 -*-
"""Parse system definition files.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


class ExecObject:
    """Describe command in system definition file.

    Describe the command to execute later during generation phase.
    """

    def __init__(self, location, dependency, *args, **kwargs):
        """Constructor."""
        assert(location)
        assert(len(args) >= 1)

        self._location = location
        self._dependency = dependency
        self._args = args
        self._kwargs = kwargs

        if not self._location.extra_information:
            self._location.extra_information = self.command()

    def command(self):
        """Name of the command to execute."""
        return self._args[0]

    def arguments(self):
        """Arguments passed to command()."""
        return self._args[1:]

    def kwargs(self):
        """Keyword arguments to command()."""
        return self._kwargs

    def set_dependency(self, dependency):
        """Set dependency."""
        self._dependency = dependency

    def dependency(self):
        """Return dependency of the system (or None)."""
        return self._dependency

    def location(self):
        """Return location."""
        return self._location

    def __str__(self):
        """Turn into string object."""
        return '{}: {},{}'.format(self._location, self._args, self._kwargs)
