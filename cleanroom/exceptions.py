#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

class CleanRoomError(RuntimeError):
    def __init__(self, msg):
        super().__init__(msg)


class PreflightError(CleanRoomError):
    pass


class ContextError(CleanRoomError):
    pass


class PrepareError(CleanRoomError):
    pass


class GenerateError(CleanRoomError):
    pass


class SystemNotFoundError(CleanRoomError):
    pass


class ParseError(CleanRoomError):
    def __init__(self, line, msg):
        self.line = line
        super().__init__(msg)


if __name__ == '__main__':
    pass
