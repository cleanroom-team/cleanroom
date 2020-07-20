# -*- coding: utf-8 -*-
"""Parse system definition files.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location


import typing


class ExecObject(typing.NamedTuple):
    location: Location
    command: str
    args: typing.Tuple[typing.Any, ...]
    kwargs: typing.Dict[str, typing.Any]
