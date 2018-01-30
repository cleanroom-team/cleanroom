#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exceptions used in cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


class CleanRoomError(RuntimeError):
    """Base class for all cleanroom Exceptions."""

    def __init__(self, msg):
        """Constructor."""
        super().__init__(msg)

    def __str__(self):
        """Stringify exception."""
        assert(len(self.args) == 1)
        return 'Error: {}'.format(self.args[0])


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

    pass


class SystemNotFoundError(CleanRoomError):
    """Error raised when a system could not be found."""

    pass


class ParseError(CleanRoomError):
    """Error raised while parsing system descriptions."""

    def __init__(self, line, msg):
        """Constructor."""
        super().__init__(line, msg)

    def __str__(self):
        """Stringify exception."""
        assert(len(self.args) == 2)
        return 'Error in line {}: {}'.format(self.args[0], self.args[1])


if __name__ == '__main__':
    pass
