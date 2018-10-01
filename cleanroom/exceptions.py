# -*- coding: utf-8 -*-
"""Exceptions used in cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .location import Location

import typing


class CleanRoomError(RuntimeError):
    """Base class for all cleanroom Exceptions."""

    def __init__(self, *args: typing.Any, location: Location=None) -> None:
        """Constructor."""
        super().__init__(*args)
        self.location = location

    def __str__(self) -> str:
        """Stringify exception."""
        prefix = 'Error'
        if self.location is not None:
            prefix += ' in {}'.format(self.location)

        return '{}: {}'.format(prefix, ' '.join(self.args))


class PreflightError(CleanRoomError):
    """Error raised in the Preflight Phase."""

    pass


class ContextError(CleanRoomError):
    """Error raised when setting up the Context to work in."""

    pass


class PrepareError(CleanRoomError):
    """Error raised while Preparing for generation."""

    pass


class GenerateError(CleanRoomError):
    """Error raised during Generation phase."""

    def __init__(self, *args: typing.Any, location: Location=None,
                 original_exception: Exception=None) -> None:
        """Constructor."""
        super().__init__(*args, location=location)
        self.original_exception = original_exception

    def __str__(self) -> str:
        """Stringify exception."""
        prefix = 'Error'
        if self.location is not None:
            prefix += ' in {}'.format(self.location)

        postfix = ''
        if self.original_exception is not None:
            if isinstance(self.original_exception, AssertionError):
                postfix = '\n    Trigger: AssertionError.'
            else:
                postfix = '\n    Trigger: ' + str(self.original_exception)

        return '{}: {}{}'.format(prefix, ' '.join(self.args), postfix)


class SystemNotFoundError(CleanRoomError):
    """Error raised when a system could not be found."""

    pass


class ParseError(CleanRoomError):
    """Error raised while parsing system descriptions."""

    pass
