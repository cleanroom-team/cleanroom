# -*- coding: utf-8 -*-
"""firejail_apps command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command

from cleanroom.exceptions import ParseError

import os.path


class FirejailAppsConfigureCommand(Command):
    """The firejail_apps command."""

    def __init__(self):
        """Constructor."""
        super().__init__('firejail_apps', syntax='<APP>+',
                         help='Firejail applications.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        if not args:
            raise ParseError('"{}" does need at least one application.'
                             .format(self.name()), location=location)
        self._validate_kwargs(location, (), **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        for a in args:
            location.set_description('Processing application {}.'
                                      .format(a))
            desktop_file = '/usr/share/applications/{}.desktop'.format(a)
            if not os.path.exists(desktop_file):
                raise ex.GenerateError('Desktop file "{}" not found.'
                                       .format(desktop_file), location=location)
            system_context.execute(location.next_line(), 'sed', '/^Exec=.*$$/ '
                                   's!^Exec=!Exec=/usr/bin/firejail !', desktop_file)
