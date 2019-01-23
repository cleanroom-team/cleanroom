# -*- coding: utf-8 -*-
"""pkg_nginx command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import typing


class PkgNginxCommand(Command):
    """The pkg_nginx command."""

    def __init__(self):
        """Constructor."""
        super().__init__('pkg_nginx', syntax='http=False https=True',
                         help_string='Setup nginx web server.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_no_args(location, *args)
        self._validate_kwargs(location, ('http', 'https',), **kwargs)
        self._require_kwargs(location, ('http', 'https',), **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        system_context.execute(location.next_line(),
                               'pacman', 'nginx')

        # Do setup:
        # Fix missing symlink:
        system_context.execute(location.next_line(), 'create',
                               '/etc/nginx/dhparams.pem',
                               '''-----BEGIN DH PARAMETERS-----
MIIBCAKCAQEAtiVyRgTKjub6YmPwk7YTp+CL6OG2zHFdUBMEUcGEsfHjPB/OXxQV
iv4tHQeOxVSoiwZi9u/zWbbttpHsAXMTJsq9EzDi7uQie8iBlOOHjK7hx7LNIABJ
BkWSliZgemdY/XwdH9ckZlDpVsqdQNftfPxPZL+HpKeSFDTNGWrp8DgcoINi0Vzt
thVUhHF8961VGsjb66z3GJyuLtpRTfpV6eji87Njy06jOwbS0gdq1mOPptxBNfmA
w4oadWDreQXxTjaq0kowz9hTk/eRgnnpb0NwZb4fTJ8oYo8m0yTHoeIWFrEDhBGR
30DFtTj6OKkkfz4tKJbcIr5+uJQZuqoXSwIBAg==
-----END DH PARAMETERS-----
''', mode=0o640)

        system_context.execute(location.next_line(), 'create',
                               '/etc/nginx/nginx.conf',
                               '''#user html;
worker_processes  1;

#error_log  logs/error.log;
#error_log  logs/error.log  notice;
#error_log  logs/error.log  info;

#pid        logs/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       mime.types;
    default_type  application/octet-stream;

    types_hash_max_size 4096;

    #log_format  main  '$$remote_addr - $$remote_user [$$time_local] "$$request" '
    #                  '$$status $$body_bytes_sent "$$http_referer" '
    #                  '"$$http_user_agent" "$$http_x_forwarded_for"';

    #access_log  logs/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    #keepalive_timeout  0;
    keepalive_timeout  65;

    #gzip  on;

    include sites-enabled/*;
}
''', mode=0o644, force=True)

        system_context.execute(location.next_line(), 'mkdir',
                               '/usr/lib/systemd/system/nginx.service.d')
        system_context.execute(location.next_line(), 'systemd_harden_unit',
                               'nginx.service')

        system_context.execute(location.next_line(), 'mkdir', '/etc/nginx/sites-available')
        system_context.execute(location.next_line(), 'mkdir', '/etc/nginx/sites-enabled')
        if kwargs.get('https', True):
            system_context.execute(location.next_line(), 'mkdir', '/etc/nginx/ssl')

        # enable the daemon (actually set up socket activation)
        system_context.execute(location.next_line(), 'systemd_enable',
                               'nginx.service')

        # Open the firewall for it:
        if kwargs.get('http', False):
            system_context.execute(location.next_line(), 'net_firewall_open_port', '80',
                                   protocol='tcp', comment='Nginx')
        if kwargs.get('https', True):
            system_context.execute(location.next_line(), 'net_firewall_open_port', '443',
                                   protocol='tcp', comment='Nginx')

            system_context.add_hook(location.next_line(), '_teardown', 'chown',
                                    '/etc/nginx/ssl', recursive=True, user='root', group='root')
            system_context.add_hook(location.next_line(), '_teardown', 'chmod', 0o644,
                                    '/etc/nginx/ssl/*-cert.pem')
            system_context.add_hook(location.next_line(), '_teardown', 'chmod', 0o640,
                                    '/etc/nginx/ssl/*-key.pem')
