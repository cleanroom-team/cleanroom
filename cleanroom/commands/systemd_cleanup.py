# -*- coding: utf-8 -*-
"""systemd_cleanup command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.exceptions import GenerateError
from cleanroom.location import Location
from cleanroom.printer import trace
from cleanroom.systemcontext import SystemContext

import os
import shutil
import typing


def _map_base(old_base: str, new_base: str, input_path: str) -> typing.Tuple[str, str]:
    assert old_base.endswith("/")

    input_path = os.path.normpath(input_path)
    if not input_path.startswith(old_base):
        return input_path, input_path

    input_relative_to_oldbase = input_path[len(old_base) :]
    output = os.path.join(new_base, input_relative_to_oldbase)

    return output, input_path


def _map_target_link(
    old_base: str, new_base: str, link: str, link_target: str
) -> typing.Tuple[str, str]:
    assert old_base.endswith("/")
    assert new_base.endswith("/")
    assert link.startswith(old_base)

    link_directory = os.path.dirname(link)

    (link, _) = _map_base(old_base, new_base, link)
    (link_target, _) = _map_base(
        old_base, new_base, os.path.join(link_directory, link_target)
    )

    if link_target.startswith(new_base):
        relative_link_target = os.path.relpath(link_target, os.path.dirname(link))
        return link, relative_link_target

    return link, link_target


def _map_host_link(
    root_directory: str, old_base: str, new_base: str, link: str, link_target: str
):
    assert root_directory.endswith("/")
    assert old_base.startswith(root_directory)
    assert new_base.startswith(root_directory)

    assert old_base.endswith("/")
    assert new_base.endswith("/")
    assert link.startswith(old_base)

    assert not link_target.startswith(root_directory)

    root_directory_length = len(root_directory) - 1  # minus last '/'

    host_old_base = old_base[root_directory_length:]
    host_new_base = new_base[root_directory_length:]
    host_link = link[root_directory_length:]

    (host_link, link_target) = _map_target_link(
        host_old_base, host_new_base, host_link, link_target
    )

    assert os.path.isabs(host_link)
    return os.path.join(root_directory, host_link[1:]), link_target


def _move_symlink(
    location: Location,
    system_context: SystemContext,
    old_base: str,
    new_base: str,
    link: str,
):
    """Move a symlink."""
    root_directory = system_context.fs_directory + "/"
    link_target = os.readlink(link)
    # normalize to /usr/lib...
    if link_target.startswith("/lib/"):
        link_target = "/usr{}".format(link_target)
    (output_link, output_link_target) = _map_host_link(
        root_directory, old_base, new_base, link, link_target
    )

    trace(
        "Moving link {}->{}: {} to {}".format(
            link, link_target, output_link, output_link_target
        )
    )
    os.makedirs(os.path.dirname(output_link), mode=0o755, exist_ok=True)

    if not os.path.isdir(os.path.dirname(output_link)):
        raise GenerateError(
            '"{}" is no directory when trying to move '
            '"{}" into /usr.'.format(output_link, link),
            location=location,
        )

    if os.path.exists(output_link):
        if not os.path.islink(output_link):
            raise GenerateError(
                '"{}" exists and is not a link when '
                'trying to move "{}" into /usr.'.format(output_link, link),
                location=location,
            )
        else:
            old_link_target = os.readlink(output_link)
            if old_link_target != output_link_target:
                raise GenerateError(
                    '"{}" exists but points to "{}" '
                    'when "{}" was expected.'.format(
                        link, old_link_target, output_link_target
                    ),
                    location=location,
                )
            else:
                os.unlink(link)
                return  # Already correct
    else:
        os.symlink(output_link_target, output_link)
        os.unlink(link)


def _move_file(location: Location, old_base: str, new_base: str, path: str):
    """Move a file."""
    path_dir = os.path.dirname(path)
    path_name = os.path.basename(path)

    new_dir = _map_base(old_base, new_base, path_dir)[0]
    if os.path.exists(new_dir) and not os.path.isdir(new_dir):
        raise GenerateError(
            '"{}" is not a directory when moving "{}".'.format(new_dir, path),
            location=location,
        )

    if not os.path.exists(new_dir):
        os.makedirs(new_dir, 0o755)

    new_path = os.path.join(new_dir, path_name)
    if os.path.exists(new_path):
        raise GenerateError(
            '"{}" already exists when moving "{}".'.format(new_path, path),
            location=location,
        )

    shutil.copyfile(path, new_path)


class SystemdCleanupCommand(Command):
    """The systemd_cleanup command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "systemd_cleanup",
            help_string="Make sure /etc/systemd/system is empty by "
            "moving files and links to the appropriate /usr "
            "directory.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        old_base = system_context.file_name("/etc/systemd/system") + "/"
        new_base = system_context.file_name("/usr/lib/systemd/system") + "/"

        trace("walking:", old_base)

        for root, _, files in os.walk(old_base):
            for f in files:
                full_path = os.path.join(root, f)
                trace("Checking", full_path)
                if os.path.islink(full_path):
                    trace("Moving link", full_path)
                    _move_symlink(
                        location, system_context, old_base, new_base, full_path
                    )
                else:
                    trace("Moving file", full_path)
                    _move_file(location, old_base, new_base, full_path)

        self._execute(
            location.next_line(),
            system_context,
            "remove",
            "/etc/systemd/system/*",
            recursive=True,
            force=True,
        )
