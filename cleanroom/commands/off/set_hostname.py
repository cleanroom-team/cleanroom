# -*- coding: utf-8 -*-
"""set_hostname command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.exceptions import GenerateError
from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import typing


class SetHostnameCommand(Command):
    """The set_hostname command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('set_hostname', syntax='<STATIC> [pretty=<PRETTY>]',
                         help_string='Set the hostname of the system.', file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs a static hostname.',
                                  *args)
        self._validate_kwargs(location, ('pretty',), **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        static_hostname = args[0]
        pretty_hostname = kwargs.get('pretty', static_hostname)

        if system_context.has_substitution('HOSTNAME'):
            raise GenerateError('Hostname was already set.', location=location)

        system_context.set_substitution('HOSTNAME', static_hostname)
        system_context.set_substitution('PRETTY_HOSTNAME', pretty_hostname)

        system_context.execute(location,
                               'create', '/etc/hostname', static_hostname)
        system_context.execute(location.next_line(), 'sed',
                               '/^PRETTY_HOSTNAME=/ cPRETTY_HOSTNAME=\"{}\"'
                               .format(pretty_hostname),
                               '/etc/machine.info')
