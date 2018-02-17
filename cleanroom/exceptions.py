#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exceptions used in cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


class CleanRoomError(RuntimeError):
    """Base class for all cleanroom Exceptions."""

    def __init__(self, *args, file_name=None, line_number=-1):
        """Constructor."""
        super().__init__(*args)
        self._file_name = file_name
        self._line_number = line_number

    def __str__(self):
        """Stringify exception."""
        prefix = 'Error'
        if self._file_name:
            if self._line_number > 0:
                prefix = 'Error in "{}"({})'.format(self._file_name,
                                                    self._line_number)
            else:
                prefix = 'Error in "{}"'.format(self._file_name)

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

    pass


class SystemNotFoundError(CleanRoomError):
    """Error raised when a system could not be found."""

    pass


class ParseError(CleanRoomError):
    """Error raised while parsing system descriptions."""

    pass


if __name__ == '__main__':
    pass
