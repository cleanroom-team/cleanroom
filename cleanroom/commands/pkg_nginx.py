# -*- coding: utf-8 -*-
"""pkg_nginx command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.helper.file import create_file
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os
import textwrap
import typing


class PkgNginxCommand(Command):
    """The pkg_nginx command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "pkg_nginx",
            syntax="http=False https=True",
            help_string="Setup nginx web server.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_no_args(location, *args)
        self._validate_kwargs(
            location,
            (
                "http",
                "https",
            ),
            **kwargs
        )
        self._require_kwargs(
            location,
            (
                "http",
                "https",
            ),
            **kwargs
        )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        self._execute(location, system_context, "pacman", "nginx")

        # Do setup:
        # Fix missing symlink:
        create_file(
            system_context,
            "/etc/nginx/dhparams.pem",
            textwrap.dedent(
                """\
                    -----BEGIN DH PARAMETERS-----
                    MIIBCAKCAQEAtiVyRgTKjub6YmPwk7YTp+CL6OG2zHFdUBMEUcGEsfHjPB/OXxQV
                    iv4tHQeOxVSoiwZi9u/zWbbttpHsAXMTJsq9EzDi7uQie8iBlOOHjK7hx7LNIABJ
                    BkWSliZgemdY/XwdH9ckZlDpVsqdQNftfPxPZL+HpKeSFDTNGWrp8DgcoINi0Vzt
                    thVUhHF8961VGsjb66z3GJyuLtpRTfpV6eji87Njy06jOwbS0gdq1mOPptxBNfmA
                    w4oadWDreQXxTjaq0kowz9hTk/eRgnnpb0NwZb4fTJ8oYo8m0yTHoeIWFrEDhBGR
                    30DFtTj6OKkkfz4tKJbcIr5+uJQZuqoXSwIBAg==
                    -----END DH PARAMETERS-----
                    """
            ).encode("utf-8"),
            mode=0o640,
        )

        create_file(
            system_context,
            "/etc/nginx/nginx.conf",
            textwrap.dedent(
                """\
                    user html;
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
                    """
            ).encode("utf-8"),
            mode=0o644,
            force=True,
        )

        os.makedirs(system_context.file_name("/usr/lib/systemd/system/nginx.service.d"))
        self._execute(
            location.next_line(),
            system_context,
            "systemd_harden_unit",
            "nginx.service",
            CapabilityBoundingSet="IGNORE",
            NoNewPrivileges=False,
            PrivateUsers=False,
        )

        os.makedirs(system_context.file_name("/etc/nginx/sites-available"))
        os.makedirs(system_context.file_name("/etc/nginx/sites-enabled"))
        if kwargs.get("https", True):
            os.makedirs(system_context.file_name("/etc/nginx/ssl"))

        # enable the daemon (actually set up socket activation)
        self._execute(
            location.next_line(), system_context, "systemd_enable", "nginx.service"
        )

        # Open the firewall for it:
        if kwargs.get("http", False):
            self._execute(
                location.next_line(),
                system_context,
                "net_firewall_open_port",
                "80",
                protocol="tcp",
                comment="Nginx",
            )
        if kwargs.get("https", True):
            self._execute(
                location.next_line(),
                system_context,
                "net_firewall_open_port",
                "443",
                protocol="tcp",
                comment="Nginx",
            )

            self._add_hook(
                location.next_line(),
                system_context,
                "_teardown",
                "chown",
                "/etc/nginx/ssl",
                recursive=True,
                user="root",
                group="root",
            )
            self._add_hook(
                location.next_line(),
                system_context,
                "_teardown",
                "chmod",
                0o644,
                "/etc/nginx/ssl/*-cert.pem",
            )
            self._add_hook(
                location.next_line(),
                system_context,
                "_teardown",
                "chmod",
                0o640,
                "/etc/nginx/ssl/*-key.pem",
            )
