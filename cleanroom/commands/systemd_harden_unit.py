# -*- coding: utf-8 -*-
"""systemd_harden_unit command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


def _trueify(value: bool) -> str:
    return 'true' if value else 'false'


class SystemdHardenUnitCommand(Command):
    """The systemd_harden_unit command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__('systemd_harden_unit',
                         syntax='<UNIT> [<UNITS>] [CapabilityBoundingSet="IGNORE"]'
                         '[NoNewPrivileges=True] [PrivateDevices=True] '
                         '[PrivateTmp=True] [PrivateUsers=True] '
                         '[ProtectControlGroups=True] [ProtectHome="true"] '
                         '[ProtectKernelModules=True] [ProtectKernelTunables=True]'
                         '[ProtectSystem="full"] [RemoveIPC=True] '
                         '[RestrictAddressFamilies="AF_UNIX AF_INET AF_INET6"] '
                         '[RestrictRealtime=True] [SystemCallArchitecture="native"] '
                         '[SystemCallFilter="@system-service"]',
                         help_string='Apply hardening override to a systemd unit.',
                         file=__file__, **services)

    def validate(self, location: Location,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Validate the arguments."""
        self._validate_args_at_least(location, 1,
                                     '"{}" needs at least one unit to harden.', *args)
        self._validate_kwargs(location, ('CapabilityBoundingSet', 'NoNewPrivileges',
                                         'PrivateDevices', 'PrivateTmp', 'PrivateUsers',
                                         'ProtoctControlGroups', 'ProtectHome',
                                         'ProtectKernelModules', 'ProtectKernelTunables',
                                         'ProtectSystem', 'RemoveIPC', 'RestrictAddressFamilies',
                                         'SystemCallArchitecture',), **kwargs)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        for unit in args:
            self._harden_unit(location, system_context, unit, **kwargs)

    def _harden_unit(self, location: Location, system_context: SystemContext, unit: str,
                     **kwargs: typing.Any) -> None:
        if '.' not in unit:
            unit += '.service'

        self._execute(location, system_context, 'mkdir',
                      '/usr/lib/systemd/system/{}.d'.format(unit), force=True,
                      mode=0o755)

        contents = '[Service]\n'
        bounding_set = kwargs.get('CapabilityBoundingSet', 'IGNORE')
        if bounding_set != 'IGNORE':
            contents += 'CapabilityBoundingSet={}\n'.format(kwargs.get('CapabilityBoundingSet', ''))
        contents += 'NoNewPrivileges={}\n'.format(_trueify(kwargs.get('NoNewPrivileges', True)))
        contents += 'PrivateDevices={}\n'.format(_trueify(kwargs.get('PrivateDevices', True)))
        contents += 'PrivateTmp={}\n'.format(_trueify(kwargs.get('PrivateTmp', True)))
        contents += 'PrivateUsers={}\n'.format(_trueify(kwargs.get('PrivateUsers', True)))
        contents += 'ProtectControlGroups={}\n'.format(_trueify(kwargs.get('ProtectControlGroups', True)))
        contents += 'ProtectHome={}\n'.format(kwargs.get('ProtectHome', 'true'))
        contents += 'ProtectKernelModules={}\n'.format(_trueify(kwargs.get('ProtectKernelModules', True)))
        contents += 'ProtectKernelTunables={}\n'.format(_trueify(kwargs.get('ProtectKernelTunables', True)))
        contents += 'ProtectSystem={}\n'.format(kwargs.get('ProtectSystem', 'full'))
        contents += 'RemoveIPC={}\n'.format(_trueify(kwargs.get('RemoveIPC', True)))
        contents += 'RestrictAddressFamilies={}\n'.format(kwargs.get('RestrictAddressFamilies', 'AF_UNIX AF_INET AF_INET6'))
        contents += 'RestrictRealtime={}\n'.format(_trueify(kwargs.get('RestrictRealtime', True)))
        contents += 'SystemCallArchitectures={}\n'.format(kwargs.get('SystemCallArchitecture', 'native'))
        contents += 'SystemCallFilter={}\n'.format(kwargs.get('SystemCallFilter', '@system-service'))

        self._execute(location, system_context, 'create',
                      '/usr/lib/systemd/system/{}.d/security.conf'.format(unit),
                      contents, mode=0o644)
