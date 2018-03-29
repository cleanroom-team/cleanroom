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

        self.file_name = file_name
        self.line_number = line_number
        self.line_offset = line_offset
        self.extra_information = extra_information

    def reset(self):
        """Reset the current command."""
        self.file_name = None
        self.line_number = None
        self.line_offset = None
        self.extra_information = None

    def is_valid(self):
        """Check whether this object contains a valid location."""
        return self.file_name is not None \
            or self.extra_information is not None

    def next_line_offset(self, message):
        """Increment line_offset and update extra_information with message."""
        if self.line_offset is None:
            self.line_offset = 0
        self.line_offset += 1
        self.extra_information = message

    def __str__(self):
        """Strigify location."""
        if self.file_name is None:
            if self.extra_information:
                return '"{}"'.format(self.extra_information)
            return '<UNKNOWN>'

        result = self.file_name

        if self.line_number is not None and self.line_number > 0:
            result += ':{}'.format(self.line_number)

        if self.line_offset is not None and self.line_offset > 0:
            result += '+{}'.format(self.line_offset)

        if self.extra_information is not None:
            result += ' "{}"'.format(self.extra_information)

        return result
