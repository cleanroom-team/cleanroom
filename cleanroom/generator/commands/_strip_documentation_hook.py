# -*- coding: utf-8 -*-
"""_strip_documentation_hook command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.generator.command import Command

from cleanroom.printer import debug

import os.path


class StripDocumentationHookCommand(Command):
    """The strip_documentation Command."""

    def __init__(self):
        """Constructor."""
        super().__init__('_strip_documentation_hook',
                         help='Strip away documentation files (hook).', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        location.set_description('Strip documentation files')
        to_remove = ['/usr/share/doc/*', '/usr/share/gtk-doc/html',
                     '/usr/share/help/*']
        if not os.path.exists(system_context.file_name('/usr/bin/man')):
            debug('No /usr/bin/man: Removing man pages.')
            to_remove += ['/usr/share/man/*',]
        if not os.path.exists(system_context.file_name('/usr/bin/info')):
            debug('No /usr/bin/info: Removing info pages.')
            to_remove += ['/usr/share/info/*',]
        system_context.execute(location, 'remove', *to_remove, recursive=True, force=True)
