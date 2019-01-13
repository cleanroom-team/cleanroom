# -*- coding: utf-8 -*-
"""strip_development_files command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.generator.command import Command

import os.path


class StripDevelopmentFilesCommand(Command):
    """The strip_development_files Command."""

    def __init__(self):
        """Constructor."""
        super().__init__('strip_development_files',
                         help='Strip away development files.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        location.set_description('Strip development files')
        system_context.add_hook(location, 'export',
                                'remove',  '/usr/include/*', '/usr/src/*',
                                '/usr/share/pkgconfig/*',
                                '/usr/lib/pkgconfig/*',
                                '/usr/share/aclocal/*', '/usr/lib/cmake/*',
                                '/usr/share/gir-1.0/*',
                                recursive=True, force=True)

        # Remove .so symlinks:
        directory = system_context.file_name('/usr/lib')
        for f in os.listdir(directory):
            fullname = os.path.join(directory, f)
            if fullname.endswith('/libnss_files.so'):
                continue
            if fullname.endswith('.a') \
              or (fullname.endswith('.so') and os.path.islink(fullname)):
                os.unlink(fullname)
