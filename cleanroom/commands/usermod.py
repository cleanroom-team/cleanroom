# -*- coding: utf-8 -*-
"""usermod command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.exceptions import ParseError
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class UsermodCommand(Command):
    """The usermod command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "usermod",
            syntax="<NAME> [comment=<COMMENT>] [home=<HOMEDIR>] "
            "[gid=<GID>] [uid=<UID>] [rename=<NEW_NAME>] "
            "[groups=<GROUP1>,<GROUP2>] [lock=False] "
            "[password=<CRYPTED_PASSWORD>] [shell=<PATH>] "
            "[expire=<EXPIRE_DATE>], [append=False]",
            help_string="Modify an existing user.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs a username.', *args)
        if len(kwargs) == 0:
            raise ParseError("usermod needs keyword arguments", location=location)

        lock = kwargs.get("lock", None)
        if lock not in (True, None, False):
            raise ParseError(
                '"lock" must be either True, False or None.', location=location
            )

        append = kwargs.get("append", False)
        if append not in (True, False):
            raise ParseError(
                '"append" must have either True or False as ' "value.",
                location=location,
            )

        if append and kwargs.get("groups", "") == "":
            raise ParseError(
                '"append" needs "groups" to be set, too.', location=location
            )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        self._service("user_helper").usermod(
            args[0], **kwargs, root_directory=system_context.fs_directory
        )
