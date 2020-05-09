# -*- coding: utf-8 -*-
"""Parse system definition files.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import collections


ExecObject = collections.namedtuple(
    "ExecObject", ["location", "command", "args", "kwargs"]
)
