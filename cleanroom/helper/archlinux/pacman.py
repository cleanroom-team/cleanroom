#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The class that drives the system generation.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file

import os
import os.path


class Pacman:
    """Drives Pacman."""

    def __init__(self, run_context):
        """Constructor."""
        self._run_context = run_context

    def global_gpg_directory(self):
        """Return the global location of the pacman GPG configuration."""
        return file.file_name(self._run_context, '/usr/lib/pacman/gpg')

    def global_db_directory(self):
        """Return the global location of the pacman DB."""
        return file.file_name(self._run_context, '/usr/lib/pacman/db')

    def cache_directory(self):
        """Return the global location of the pacman cache."""
        return file.file_name(self._run_context, '/var/cache/pacman/pkgs')

    def initial_pacstrap_configuration_file(self, run_context):
        """Return the global configuration for initial pacstrap run."""
        init_config_path = os.path.join(
            self._run_context.system_definition_directory(),
            'pacstrap.conf')
        if not os.path.isfile(init_config_path):
            raise ex.GenerateError('Could not find: "{}".'
                                   .format(init_config_path))
        return init_config_path


if __name__ == '__main__':
    pass
