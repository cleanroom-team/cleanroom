# -*- coding: utf-8 -*-
"""set_locales command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.exceptions import ParseError
from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import os.path
import typing


class SetLocalesCommand(Command):
    """The set_locales command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('set_locales',
                         syntax='<LOCALE> [<MORE_LOCALES>] [charmap=UTF-8]',
                         help_string='Set the system locales.', file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_args_at_least(location, 1,
                                     '"{}" needs at least one locale.', *args)
        self._validate_kwargs(location, ('charmap',), **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        charmap = kwargs.get('charmap', 'UTF-8')
        locales_dir = os.path.join(system_context.fs_directory(),
                                   'usr/share/locale')
        locales = []
        for a in args:
            if not os.path.isdir(os.path.join(locales_dir, a))\
               and not os.path.isdir(os.path.join(locales_dir, a[0:2])):
                raise ParseError('Locale "{}" not found in /usr/share/locale.'
                                 .format(a), location=location)
            locales.append('{}.{} {}\n'.format(a, charmap, charmap))

        system_context.execute(location,
                               'append', '/etc/locale.gen', ''.join(locales),
                               force=True)
        self._setup_hooks(location, system_context, locales)

    def _setup_hooks(self, location: Location, system_context: SystemContext,
                     locales: typing.Sequence[str]) -> None:
        if not system_context.has_substitution('CLRM_LOCALES'):
            location.set_description('run locale-gen')
            system_context.add_hook(location, 'export',
                                    'run', '/usr/bin/locale-gen')
            location.set_description('Remove locale related data.')
            system_context.add_hook(location, 'export',
                                    'remove', '/usr/share/locale/*',
                                    '/etc/locale.gen', '/usr/bin/locale-gen',
                                    '/usr/bin/localedef',
                                    force=True, recursive=True)
            system_context.set_substitution('CLRM_LOCALES', ','.join(locales))
