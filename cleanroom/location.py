# -*- coding: utf-8 -*-
"""The class that holds a location in source.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from __future__ import annotations

import typing


class Location:
    """Context data for the execution os commands."""

    def __init__(self, *,
                 file_name: typing.Optional[str] = None,
                 line_number: typing.Optional[int] = None,
                 description: typing.Optional[str] = None,
                 parent: Location = None) -> None:
        """Constructor."""
        if line_number is not None:
            assert line_number > 0
            assert file_name is not None

        self.file_name = file_name
        self.line_number = line_number
        self.description = description
        self.parent = parent

    def is_valid(self) -> bool:
        """Check whether this object contains a valid location."""
        return self.file_name is not None \
            or self.description is not None

    def set_description(self, message: str) -> None:
        """Set location description."""
        self.description = message

    def create_child(self, *, file_name: typing.Optional[str] = None,
                     line_number: typing.Optional[int] = None,
                     description: typing.Optional[str] = None) -> 'Location':
        return Location(file_name=file_name,
                        line_number=line_number,
                        description=description,
                        parent=self)

    def next_line(self) -> 'Location':
        if self.line_number is None:
            self.line_number = 1
        else:
            self.line_number += 1
        return self

    def __str__(self) -> str:
        """Stringify location."""
        if self.file_name is None:
            if self.description:
                result = '"{}"'.format(self.description)
            else:
                result = '<UNKNOWN>'

        else:
            result = self.file_name

            if self.line_number is not None and self.line_number > 0:
                result += ':{}'.format(self.line_number)

            if self.description is not None:
                result += ' "{}"'.format(self.description)

        if self.parent is not None:
            result = str(self.parent) + " => " + result
        return result
