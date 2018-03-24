# -*- coding: utf-8 -*-
"""The class that holds a location in source.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


class Location:
    """Context data for the execution os commands."""

    def __init__(self, *, file_name=None,
                 line_number=None, line_offset=None,
                 extra_information=None):
        """Constructor."""
        if line_number is not None:
            assert(line_number > 0)
            assert(file_name is not None)
        if line_offset is not None:
            assert(line_offset > 0)
            assert(line_number is not None)

        self._file_name = file_name
        self._line_number = line_number
        self._line_offset = line_offset
        self._extra_information = extra_information

    def reset(self):
        """Reset the current command."""
        self._file_name = None
        self._line_number = None
        self._line_offset = None
        self._extra_information = None

    def __str__(self):
        """Strigify location."""
        if self._file_name is None:
            if self._extra_information:
                return '"{}"'.format(self._extra_information)
            return '<UNKNOWN>'

        result = self._file_name

        if self._line_number is not None and self._line_number > 0:
            result += ':{}'.format(self._line_number)

        if self._line_offset is not None and self._line_offset > 0:
            result += '+{}'.format(self._line_offset)

        if self._extra_information is not None:
            result += ' "{}"'.format(self._extra_information)

        return result
