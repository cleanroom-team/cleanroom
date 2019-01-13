# -*- coding: utf-8 -*-
"""strip_documentation command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.generator.command import Command

from cleanroom.printer import debug

import os.path


class StripDocumentationCommand(Command):
    """The strip_documentation Command."""

    def __init__(self):
        """Constructor."""
        super().__init__('strip_documentation',
                         help='Strip away documentation files.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        system_context.add_hook(location, 'export', '_strip_documentation_hook')
