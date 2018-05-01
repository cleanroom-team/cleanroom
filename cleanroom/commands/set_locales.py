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
                         help='Set the system locales.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_at_least(location, 1,
                                     '"{}" needs at least one locale.', *args)
        self._validate_kwargs(location, ('charmap',), **kwargs)

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
        self._setup_hooks(location, system_context, locales)

    def _setup_hooks(self, location, system_context, locales):
        if not system_context.has_substitution('CLRM_LOCALES'):
            location.next_line_offset('run locale-gen')
            system_context.add_hook(location, 'export',
                                    'run', '/usr/bin/locale-gen')
            location.next_line_offset('Remove locale related data.')
            system_context.add_hook(location, 'export',
                                    'remove', '/usr/share/locale/*',
                                    '/etc/locale.gen', '/usr/bin/locale-gen',
                                    '/usr/bin/localedef',
                                    force=True, recursive=True)
        system_context.set_substitution('CLRM_LOCALES', locales)
