# -*- coding: utf-8 -*-
"""Exceptions used in cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .location import Location

import typing


class CleanRoomError(Exception):
    """Base class for all cleanroom Exceptions."""

    def __init__(
        self,
        *args: typing.Any,
        location: typing.Optional[Location] = None,
        original_exception: typing.Optional[Exception] = None
    ) -> None:
        """Constructor."""
        super().__init__(*args)
        self.location = location
        self.original_exception = original_exception

    def set_location(self, location: Location):
        self.location = location

    def __str__(self) -> str:
        """Stringify exception."""
        prefix = "Error"
        if self.location:
            prefix += " in {}".format(self.location)

        postfix = ""
        if self.original_exception is not None:
            if isinstance(self.original_exception, AssertionError):
                postfix = "\n    Trigger: AssertionError."
            else:
                postfix = "\n    Trigger: " + str(self.original_exception)

        return "{}: {}{}".format(prefix, super().__str__(), postfix)


class PreflightError(CleanRoomError):
    """Error raised in the Preflight Phase."""

    pass


class ParseError(CleanRoomError):
    """Error raised while parsing system descriptions."""

    pass


class GenerateError(CleanRoomError):
    """Error raised during Generation phase."""

    pass


class SystemNotFoundError(CleanRoomError):
    """Error raised when a system could not be found."""

    pass
