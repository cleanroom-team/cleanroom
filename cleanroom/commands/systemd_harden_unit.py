# -*- coding: utf-8 -*-
"""systemd_harden_unit command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import typing


def _trueify(value: bool) -> str:
    return 'true' if value else 'false'


def _harden_unit(location: Location, system_context: SystemContext, unit: str,
                 **kwargs: typing.Any) -> None:
    if '.' not in unit:
        unit += '.service'

    system_context.execute(location, 'mkdir',
                           '/usr/lib/systemd/system/{}.d'.format(unit),
                           force=True, mode=0o755)
    contents = '[Unit]\n'
    contents += 'CapabilityBoundingSet={}\n'.format(kwargs.get('CapabilityBoundingSet', ''))
    contents += 'NoNewPrivileges={}\n'.format(_trueify(kwargs.get('NoNewPriviledges', True)))
    contents += 'PrivateDevices={}\n'.format(_trueify(kwargs.get('PrivateDevices', True)))
    contents += 'PrivateTmp={}\n'.format(_trueify(kwargs.get('PrivateTmp', True)))
    contents += 'PrivateUsers={}\n'.format(_trueify(kwargs.get('PrivateUsers', True)))
    contents += 'ProtectControlGroups={}\n'.format(_trueify(kwargs.get('ProtectControlGroups', True)))
    contents += 'ProtectHome={}\n'.format(kwargs.get('ProtectHome', 'tmpfs'))
    contents += 'ProtectKernelModules={}\n'.format(_trueify(kwargs.get('ProtectKernelModules', True)))
    contents += 'ProtectKernelTunables={}\n'.format(_trueify(kwargs.get('ProtectKernelTunables', True)))
    contents += 'ProtectSystem={}\n'.format(kwargs.get('ProtectSystem', 'full'))
    contents += 'RemoveIPC={}\n'.format(_trueify(kwargs.get('RemoveIPC', True)))
    contents += 'RestrictAddressFamilies={}\n'.format(kwargs.get('RestrictAddressFamilies', 'AF_UNIX AF_INET AF_INET6'))
    contents += 'RestrictRealtime={}\n'.format(_trueify(kwargs.get('RestrictRealtime', True)))
    contents += 'SystemCallArchitecture={}\n'.format(kwargs.get('SystemCallArchitecture', 'native'))
    contents += 'SystemCallFilter={}\n'.format(kwargs.get('SystemCallFilter', '@system-service'))

    system_context.execute(location, 'create',
                           '/usr/lib/systemd/system/{}.d/security.conf'.format(unit),
                           contents, mode=0o644)


class SystemdHardenUnitCommand(Command):
    """The systemd_harden_unit command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('systemd_harden_unit',
                         syntax='<UNIT> [<UNITS>] [CapabilityBoundingSet=""]'
                         '[NoNewPriviledges=True] [PrivateDevices=True] '
                         '[PrivateTmp=True] [ProtectControlGroups=True] [ProtectHome="tmpfs"] '
                         '[ProtectKernelModules=True] [ProtectKernelTunables=True]'
                         '[ProtectSystem="full"] [RemoveIPC=True] '
                         '[RestrictAddressFamilies="AF_UNIX AF_INET AF_INET6"] '
                         '[RestrictRealtime=True] [SystemCallArchitecture="native"] '
                         '[SystemCallFilter="@system-service"]',
                         help_string='Apply hardening override to a systemd unit.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_args_at_least(location, 1,
                                     '"{}" needs at least one unit to harden.', *args)
        self._validate_kwargs(location, ('CapabilityBoundingSet', 'NoNewPriviledges',
                                         'PrivateDevices', 'PrivateTmp',
                                         'ProtoctControlGroups', 'ProtectHome',
                                         'ProtectKernelModules', 'ProtectKernelTunables',
                                         'ProtectSystem', 'RemoveIPC', 'RestrictAddressFamilies',
                                         'SystemCallArchitecture',), **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        for unit in args:
            _harden_unit(location, system_context, unit, **kwargs)
