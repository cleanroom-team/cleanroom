# -*- coding: utf-8 -*-
"""set_locales command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex

import os.path


class SetLocalesCommand(cmd.Command):
    """The set_locales command."""

    def __init__(self):
        """Constructor."""
        super().__init__('set_locales',
                         syntax='<LOCALE> [<MORE_LOCALES>] [charmap=UTF-8]',
                         help='Set the system locales.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        if len(args) < 1:
            raise ex.ParseError('set_locales needs at least one locale.',
                                location=location)
        return None

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        charmap = kwargs.get('charmap', 'UTF-8')
        locales_dir = os.path.join(system_context.fs_directory(),
                                   'usr/share/locale')
        locales = []
        for a in args:
            if not os.path.isdir(os.path.join(locales_dir, a))\
               and not os.path.isdir(os.path.join(locales_dir, a[0:2])):
                raise ex.ParseError('Locale "{}" not found in '
                                    '/usr/share/locale.'.format(a),
                                    location=location)
            locales.append('{}.{} {}'.format(a, charmap, charmap))

        system_context.execute(location,
                               'create', '/etc/locale.gen', '\n'.join(locales),
                               force=True)
        self._setup_hooks(system_context, location)

    def _setup_hooks(self, system_context, location):
        locales_flag = 'locales_set_up'
        if not system_context.flags.get(locales_flag, False):
            location.next_line_offset('run locale-gen')
            system_context.add_hook('export', location,
                                    'run', '/usr/bin/locale-gen')
            location.next_line_offset('Remove locale related data.')
            system_context.add_hook('export', location,
                                    'remove', '/usr/share/locale/*',
                                    '/etc/locale.gen', '/usr/bin/locale-gen',
                                    '/usr/bin/localedef',
                                    force=True, recursive=True)
        system_context.flags[locales_flag] = True
