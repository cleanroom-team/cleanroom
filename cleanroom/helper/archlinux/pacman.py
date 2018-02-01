#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The class that drives the system generation.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.helper.generic.file as file


class Pacman:
    """Drives Pacman."""

    def __init__(self, run_context):
        """Constructor."""
        self._run_context = run_context

    def gpg_directory(self):
        """Return the location of the pacman GPG configuration."""
        return file.file_name(self._run_context, '/usr/lib/pacman/gpg')

    def db_directory(self):
        """Return the location of the pacman DB."""
        return file.file_name(self._run_context, '/usr/lib/pacman/db')

    def cache_directory(self):
        """Return the location of the pacman cache."""
        return file.file_name(self._run_context, '/var/cache/pacman/pkgs')


if __name__ == '__main__':
    pass
