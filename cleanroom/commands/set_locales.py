# -*- coding: utf-8 -*-
"""set_locales command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.exceptions import ParseError
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os.path
import typing


class SetLocalesCommand(Command):
    """The set_locales command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "set_locales",
            syntax="<LOCALE> [<MORE_LOCALES>] [charmap=UTF-8]",
            help_string="Set the system locales.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_args_at_least(
            location, 1, '"{}" needs at least one locale.', *args
        )
        self._validate_kwargs(location, ("charmap",), **kwargs)

    def register_substitutions(self) -> typing.List[typing.Tuple[str, str, str]]:
        return [
            (
                "CLRM_LOCALES",
                "",
                "Comma-separated list of locales set up by set_locales command.",
            ),
        ]

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        charmap = kwargs.get("charmap", "UTF-8")
        locales_dir = system_context.file_name("/usr/share/locale")
        locales = []
        for a in args:
            if not os.path.isdir(os.path.join(locales_dir, a)) and not os.path.isdir(
                os.path.join(locales_dir, a[0:2])
            ):
                raise ParseError(
                    f'Locale "{a}" not found in /usr/share/locale.',
                    location=location,
                )
            locales.append(f"{a}.{charmap} {charmap}\n")

        self._execute(
            location,
            system_context,
            "append",
            "/etc/locale.gen",
            "".join(locales),
            force=True,
        )
        self._setup_hooks(location, system_context, locales)

    def _setup_hooks(
        self,
        location: Location,
        system_context: SystemContext,
        locales: typing.Sequence[str],
    ) -> None:
        if not system_context.substitution("CLRM_LOCALES", ""):
            location.set_description("run locale-gen")
            self._add_hook(
                location,
                system_context,
                "export",
                "run",
                "/usr/bin/locale-gen",
                inside=True,
            )
            location.set_description("Remove locale related data.")
            self._add_hook(
                location,
                system_context,
                "export",
                "remove",
                "/usr/share/locale/*",
                "/etc/locale.gen",
                "/usr/bin/locale-gen",
                "/usr/bin/localedef",
                force=True,
                recursive=True,
            )
            system_context.set_substitution("CLRM_LOCALES", ",".join(locales))
