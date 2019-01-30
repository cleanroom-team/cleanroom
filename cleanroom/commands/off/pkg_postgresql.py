# -*- coding: utf-8 -*-
"""pkg_postgresql command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import typing


class PkgPostgresqlCommand(Command):
    """The pkg_postgresql command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('pkg_postgresql', help_string='Setup postgresql.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_no_args(location, *args)
        self._validate_kwargs(location, ('password',), **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        password = kwargs.get('password', '')
        system_context.execute(location.next_line(),
                               'pacman', 'postgresql', 'postgresql-old-upgrade')

        system_context.execute(location.next_line(),
                               'mkdir',
                               '/usr/lib/systemd/system/postgresql.service.d/',
                               mode=0o755)
        system_context.execute(location.next_line(),
                               'systemd_harden_unit', 'postgresql.service')
        system_context.execute(location.next_line(),
                               'create', '/usr/local/bin/setup-postgresql.sh',
                               '''#!/usr/bin/bash

DATADIR="$$1"
test "x$$DATADIR" = "x" && exit 2

USER=postgres
PASSWD=$$(cat /home/postgres/.pgpass | cut -d':' -f5)

if test ! -d "$${DATADIR}" ; then
    su $${USER} -c "/usr/bin/initdb -D $${DATADIR} --encoding UTF8 --locale C" || exit 1

    su $${USER} -c "/usr/bin/postgres --single -D $${DATADIR}" <<EOF > /dev/null 2>&1
    ALTER USER $${USER} PASSWORD "$${PASSWD}";
    EOF

    echo >> "$${DATADIR}/postgresql.conf"
    echo "listen_addresses = '*' # Listen everywhere!" >> "$${DATADIR}/postgresql.conf"

    cat << END_OF_CONFIG > "$${DATADIR}/pg_hba.conf"
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     md5
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
host    all             all             172.17.0.0/16           md5
# IPv6 local connections:
host    all             all             ::1/128                 md5
END_OF_CONFIG
fi
''',
                               mode=0o755)

        system_context.execute(location.next_line(),
                               'usermod', 'postgres',
                               shell='/usr/bin/bash', home='/home/postgres')

        system_context.execute(location.next_line(),
                               'mkdir', '/home/postgres',
                               mode=0o755, user='postgres', group='postgres')
        if password:
            system_context.execute(location.next_line(),
                                   'create', '/home/postgres/.pgpass',
                                   '*:*:*:*:{}'.format(password),
                                   mode=0o600, user='postgres', group='postgres')
