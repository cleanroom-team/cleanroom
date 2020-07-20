# -*- coding: utf-8 -*-
"""group manipulation print_commands.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .run import run

import os
import typing


class Group(typing.NamedTuple):
    name: str
    password: str
    gid: int
    members: typing.List[str]


def _group_data(group_file: str, name: str) -> typing.Optional[Group]:
    if not os.path.exists(group_file):
        return None

    with open(group_file, "r") as group:
        for line in group:
            if line.endswith("\n"):
                line = line[:-1]
            current_group: typing.Any = line.split(":")
            if current_group[0] == name:
                current_group[2] = int(current_group[2])
                if current_group[3] == "":
                    current_group[3] = []
                else:
                    current_group[3] = list(current_group[3].split(","))
                return Group(*current_group)
    return Group("nobody", "x", 65534, [])


class GroupHelper:
    def __init__(self, add_command: str, mod_command: str) -> None:
        self._add_command = add_command
        self._mod_command = mod_command

    def groupadd(
        self,
        group_name: str,
        *,
        gid: int = -1,
        force: bool = False,
        system: bool = False,
        root_directory: str
    ) -> bool:
        """Execute command."""
        command_line = [self._add_command, "--prefix", root_directory, group_name]

        if gid >= 0:
            command_line += ["--gid", str(gid)]

        if force:
            command_line += ["--force"]

        if system:
            command_line += ["--system"]

        return run(*command_line).returncode == 0

    @staticmethod
    def group_data(name: str, *, root_directory: str) -> typing.Optional[Group]:
        """Get group data from group file."""
        return _group_data(os.path.join(root_directory, "etc/group"), name)

    def groupmod(
        self,
        group_name: str,
        *,
        gid: int = -1,
        password: str = "",
        rename: str = "",
        root_directory: str = ""
    ) -> bool:
        """Modify an existing group."""
        command_line = [self._mod_command, "--prefix", root_directory, group_name]

        if gid >= 0:
            command_line += ["--gid", str(gid)]

        if rename:
            command_line += ["--new-name", rename]

        if password:
            command_line += ["--password", password]

        return run(*command_line).returncode == 0
