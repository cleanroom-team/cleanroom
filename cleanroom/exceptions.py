#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exceptions used in cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


class CleanRoomError(RuntimeError):
    """Base class for all cleanroom Exceptions."""

    def __init__(self, *args, run_context=None,
                 file_name=None, line_number=-1, line_offset=-1):
        """Constructor."""
        super().__init__(*args)
        if run_context is None:
            self._file_name = file_name
            self._line_number = line_number
            self._line_offset = line_offset
        else:
            assert(file_name is None)
            self._file_name = run_context.file_name
            self._line_number = run_context.line_number
            self._line_offset = run_context.line_offset

    def __str__(self):
        """Stringify exception."""
        prefix = 'Error'
        if self._file_name:
            if self._line_number > 0:
                if (self._line_offset > 0):
                    prefix = 'Error in "{}"({}-{})'.format(self._file_name,
                                                           self._line_number,
                                                           self._line_offset)
                else:
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
