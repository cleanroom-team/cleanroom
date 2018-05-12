# -*- coding: utf-8 -*-
"""Helpers for handling discs and partitions.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


def normalize_size(size):
    if isinstance(size, int):
        return size
    factor = 1
    if isinstance(size, str):
        unit = size[-1:].lower()
        number_string = size[:-1]
        if unit == 'b':
            pass
        elif unit == 'k':
            factor = 1024
        elif unit == 'm':
            factor = 1024 * 1024
        elif unit == 'g':
            factor = 1024 * 1024 * 1024
        elif unit == 't':
            factor = 1024 * 1024 * 1024 * 1024
        elif '0' <= unit <= '9':
            number_string += unit
        else:
            raise ValueError()

        number = int(number_string)
        if number < 1:
            raise ValueError()

        return number * factor


def create_image_file(file_name, size):
    size = normalize_size(size)
    with open(file_name, 'wb') as f:
        f.seek(size - 1)
        f.write(b'\0')

