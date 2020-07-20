# -*- coding: utf-8 -*-
"""user print_commands.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .run import run

import os
import typing


class User(typing.NamedTuple):
    name: str
    password: str
    uid: int
    gid: int
    comment: str
    home: str
    shell: str


def _user_data(passwd_file: str, name: str) -> typing.Optional[User]:
    if not os.path.isfile(passwd_file):
        return None
    with open(passwd_file, "r") as passwd:
        for line in passwd:
            if line.endswith("\n"):
                line = line[:-1]
            current_user: typing.List[typing.Any] = line.split(":")
            if current_user[0] == name:
                current_user[2] = int(current_user[2])
                current_user[3] = int(current_user[3])
                return User(*current_user)

    if name == "root":
        return User("root", "x", 0, 0, "root", "/root", "/usr/bin/bash")
    return User("nobody", "x", 65534, 65534, "Nobody", "/", "/sbin/nologin")


class UserHelper:
    def __init__(self, add_command: str, mod_command: str) -> None:
        self._add_command = add_command
        self._mod_command = mod_command

    def useradd(
        self,
        user_name: str,
        *,
        comment: str = "",
        home: str = "",
        gid: int = -1,
        uid: int = -1,
        shell: str = "",
        groups: str = "",
        password: str = "",
        expire: typing.Optional[str] = None,
        root_directory: str
    ):
        """Add a new user to the system."""
        command = [self._add_command, "--prefix", root_directory, user_name]

        if comment:
            command += ["--comment", comment]

        if home:
            command += ["--home", home]

        if gid >= 0:
            command += ["--gid", str(gid)]

        if uid >= 0:
            command += ["--uid", str(uid)]

        if shell:
            command += ["--shell", shell]

        if groups:
            command += ["--groups", groups]

        if password:
            command += ["--password", password]

        if expire is not None:
            if expire == "None":
                command.append("--expiredate")
            else:
                command += ["--expiredate", expire]

        return run(*command).returncode == 0

    def usermod(
        self,
        user_name: str,
        *,
        comment: str = "",
        home: str = "",
        gid: int = -1,
        uid: int = -1,
        lock: typing.Optional[bool] = None,
        rename: str = "",
        shell: str = "",
        append: bool = False,
        groups: str = "",
        password: str = "",
        expire: typing.Optional[str] = None,
        root_directory: str
    ) -> bool:
        """Modify an existing user."""
        command = [self._mod_command, "--prefix", root_directory, user_name]

        if comment:
            command += ["--comment", comment]

        if home:
            command += ["--home", home]

        if gid >= 0:
            command += ["--gid", str(gid)]

        if uid >= 0:
            command += ["--uid", str(uid)]

        if lock is not None:
            if lock:
                command.append("--lock")
            else:
                command.append("--unlock")

        if expire is not None:
            if expire == "None":
                command.append("--expiredate")
            else:
                command += ["--expiredate", expire]

        if shell:
            command += ["--shell", shell]

        if rename:
            command += ["--login", rename]

        if append:
            command.append("--append")

        if groups:
            command += ["--groups", groups]

        if password:
            command += ["--password", password]

        if expire is not None:
            command += ["--expiredate", expire]

        return run(*command).returncode == 0

    @staticmethod
    def user_data(name: str, *, root_directory: str) -> typing.Optional[User]:
        """Get user data from passwd file."""
        return _user_data(os.path.join(root_directory, "etc/passwd"), name)
