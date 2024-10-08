# -*- coding: utf-8 -*-
"""Helpers for file system actions.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from ..exceptions import GenerateError
from ..printer import debug, info, trace, verbose
from ..systemcontext import SystemContext
from .group import GroupHelper
from .user import UserHelper

from distutils.dir_util import copy_tree

import glob
import os
import os.path
import shutil
import typing


def size_extend(file: str) -> None:
    size = os.path.getsize(file)
    block_size = 1024 * 1024  # 1 MiB
    to_add = block_size - (size % block_size)
    if to_add == 0:
        return

    with open(file, "ab") as f:
        f.write(b"\0" * to_add)


def file_size(system_context: typing.Optional[SystemContext], f: str) -> int:
    f = file_name(system_context, f)
    if f and os.path.isfile(f):
        statinfo = os.stat(f)
        return statinfo.st_size
    return 0


def file_name(system_context: typing.Optional[SystemContext], f: str) -> str:
    """Return the full (outside) file path to a absolute (inside) file."""
    if not os.path.isabs(f):
        raise GenerateError(f'File path "{f}" is not absolute.')

    full_path = os.path.normpath(f)
    if system_context:
        root_path = os.path.realpath(system_context.fs_directory)
        full_path = os.path.normpath(os.path.join(root_path, f[1:]))

        if full_path != root_path and not full_path.startswith(root_path + "/"):
            raise GenerateError(f'File path "{full_path}" is outside of "{root_path}"')

    trace(f'Mapped file path "{f}" to "{full_path}".')

    return full_path


def expand_files(
    system_context: typing.Optional[SystemContext], *files: str, recursive: bool = False
) -> typing.Generator[str, None, None]:
    """Prepend the system directory and expand glob patterns.

    Prepend system directory to files iff the system_context is given.
    Expand glob patterns.
    """

    def func(f: str):
        if system_context:
            return file_name(system_context, f)
        if os.path.isabs(f):
            return f
        return os.path.join(os.getcwd(), f)

    to_iterate = map(func, files)

    for pattern in to_iterate:
        debug(f"expand_files: Matching pattern: {pattern}.")
        for match in glob.iglob(pattern, recursive=recursive):
            debug(f"expand_files: --- match {match}.")
            yield match


def _check_file(
    system_context: SystemContext,
    f: str,
    op: typing.Callable[..., bool],
    description: str,
    work_directory: typing.Optional[str] = None,
) -> bool:
    """Run op on a file f."""
    old_work_directory = os.getcwd()
    if work_directory is not None:
        work_directory = file_name(system_context, work_directory)
        os.chdir(work_directory)

    to_test = f
    if os.path.isabs(f):
        to_test = file_name(system_context, f)

    result = op(to_test)

    # Report result:
    if work_directory is None:
        trace(f"{description}: {to_test} = {result}")
    else:
        trace(f"{description}: {to_test} (relative to {work_directory}) = {result}")

    os.chdir(old_work_directory)
    return result


def exists(
    system_context: SystemContext, f: str, work_directory: typing.Optional[str] = None
) -> bool:
    """Check whether a file exists."""
    return _check_file(
        system_context, f, os.path.exists, "file exists:", work_directory=work_directory
    )


def isfile(
    system_context: SystemContext, f: str, work_directory: typing.Optional[str] = None
) -> bool:
    """Check whether a file exists and is a file."""
    return _check_file(
        system_context, f, os.path.isfile, "isfile:", work_directory=work_directory
    )


def isdir(
    system_context: SystemContext, f: str, work_directory: typing.Optional[str] = None
) -> bool:
    """Check whether a file exists and is a directory."""
    return _check_file(
        system_context, f, os.path.isdir, "isdir:", work_directory=work_directory
    )


def symlink(
    system_context: SystemContext,
    source: str,
    destination: str,
    work_directory: typing.Optional[str] = None,
) -> None:
    """Create a symbolic link."""
    if work_directory is not None:
        os.chdir(file_name(system_context, work_directory))

    if os.path.isabs(destination):
        destination = file_name(system_context, destination)

    if os.path.isdir(destination):
        destination = os.path.join(destination, os.path.basename(source))

    trace(f'Symlinking "{source}"->"{destination}".')
    os.symlink(source, destination)


def makedirs(
    system_context: SystemContext,
    *dirs: str,
    user: int = 0,
    group: int = 0,
    mode: typing.Optional[int] = None,
    exist_ok: bool = False,
) -> None:
    """Make directories in the system filesystem."""
    for d in dirs:
        info(
            f'Creating "{d}" with mode={mode}, uid={user}, gid={group} (exist_ok: {exist_ok}).'
        )
        full_path = file_name(system_context, d)
        os.makedirs(full_path, exist_ok=exist_ok)
        if mode:
            _chmod(mode, full_path)
        _chown(
            _get_uid(system_context, user), _get_gid(system_context, group), full_path
        )


def _chmod(mode: int, *files: str) -> None:
    """For internal use only."""
    if mode is None:
        return
    for f in files:
        trace(f'Chmod of "{f}" to {mode}.')
        if os.path.islink(f):
            debug(f" -> {f} is a symlink, skipping for chmod.")
            continue
        os.chmod(f, mode)


def chmod(
    system_context: SystemContext, mode: int, *files: str, recursive: bool = False
) -> None:
    """Chmod in the system filesystem."""
    _chmod(mode, *expand_files(system_context, *files, recursive=recursive))


def _chown(uid: int, gid: int, *files: str) -> None:
    """Change owner of files."""
    assert uid is not str
    assert gid is not str

    for f in files:
        trace(f'Chown of "{f}" to {uid}:{gid}.')
        os.chown(f, uid, gid, follow_symlinks=False)


def _get_uid(system_context: SystemContext, user: typing.Any) -> int:
    if user is None:
        trace("UID: Mapped None to 0.")
        return 0
    if isinstance(user, int):
        trace(f"UID: Mapped numeric user to {user}.")
        return user
    if isinstance(user, str) and user.isdigit():
        uid = int(user)
        trace(f"UID: Mapped numeric string to {uid}.")
        return uid
    data = UserHelper.user_data(user, root_directory=system_context.fs_directory)
    if data is None:  # No user file was found!
        info("UID: User file not found, mapped to 0.")
        return 0
    trace(f"UID: User name {user} mapped to {data.gid}.")
    return data.uid


def _get_gid(system_context: SystemContext, group: typing.Any) -> int:
    if group is None:
        trace("GID: Mapped None to 0.")
        return 0
    if isinstance(group, int):
        trace(f"GID: Mapped numeric group to {group}.")
        return group
    if isinstance(group, str) and group.isdigit():
        gid = int(group)
        trace(f"GID: Mapped numeric string to {gid}.")
        return gid
    data = GroupHelper.group_data(group, root_directory=system_context.fs_directory)
    if data is None:  # No group file was found!
        info("GID: Group file not found, mapped to 0.")
        return 0
    trace(f"GID: Group name {group} mapped to {data.gid}.")
    return data.gid


def chown(
    system_context: SystemContext,
    user: typing.Any,
    group: typing.Any,
    *files: str,
    recursive: bool = False,
) -> None:
    """Change ownership of a file in the system filesystem."""
    _chown(
        _get_uid(system_context, user),
        _get_gid(system_context, group),
        *expand_files(system_context, *files, recursive=recursive),
    )


def read_file(system_context: SystemContext, file: str, outside: bool = False) -> bytes:
    """Read the contents of a file."""
    if not outside:
        file = system_context.file_name(file)
    with open(file, "rb") as f:
        return f.read()


def create_file(
    system_context: SystemContext,
    file: str,
    contents: bytes,
    force: bool = False,
    mode: int = 0o644,
    user: typing.Any = 0,
    group: typing.Any = 0,
) -> None:
    """Create a new file with the given contents."""
    full_path = file_name(system_context, file)

    if os.path.exists(full_path) and not force:
        raise GenerateError(
            f'"{full_path}" exists when trying to create a ' "file there."
        )

    with open(full_path, "wb") as f:
        f.write(contents)

    trace(f"Changing permissions of {full_path} to {mode}.")
    os.chmod(full_path, mode)
    uid = _get_uid(system_context, user)
    gid = _get_gid(system_context, group)
    trace(f"Changing ownership of {full_path} to {uid}:{gid}.")
    _chown(uid, gid, full_path)


def append_file(
    system_context: SystemContext, file: str, contents: bytes, *, force: bool = False
) -> None:
    """Append contents to an existing file."""
    full_path = file_name(system_context, file)

    if not os.path.exists(full_path) and not force:
        raise GenerateError(
            f'"{full_path}" does not exist when trying to append to it.'
        )

    with open(full_path, "ab") as f:
        f.write(contents)


def prepend_file(
    system_context: SystemContext, file: str, contents: bytes, *, force: bool = False
) -> None:
    """Prepend contents to an existing file."""
    full_path = file_name(system_context, file)

    if not os.path.exists(full_path) and not force:
        raise GenerateError(
            f'"{full_path}" does not exist when trying to append to it.'
        )

    with open(full_path, "r+b") as f:
        existing_contents = f.read()
        f.seek(0, 0)
        f.write(contents + existing_contents)


def _file_op(
    system_context: typing.Optional[SystemContext],
    op: typing.Callable[..., None],
    description: str,
    *args: str,
    to_outside: bool = False,
    from_outside: bool = False,
    ignore_missing_sources: bool = True,
    force: bool = False,
    **kwargs: typing.Any,
) -> None:
    assert not to_outside or not from_outside
    sources = args[:-1]
    destination = args[-1]

    desc = description.format(sources, destination)
    debug(f"File_op(raw): {desc}")
    sources = tuple(
        expand_files(None if from_outside else system_context, *sources, recursive=True)
    )
    destination = file_name(None if to_outside else system_context, destination)
    desc = description.format(sources, destination)
    debug(f"File_op(mapped): {desc}.")

    assert sources or ignore_missing_sources

    trace(description.format('", "'.join(sources), destination))
    for source in sources:
        if not source:
            if ignore_missing_sources:
                continue
            else:
                raise OSError("Source failed to map.")

        s = os.path.normpath(source)
        if not os.path.exists(s):
            if ignore_missing_sources:
                continue
            else:
                raise OSError(f'Source file "{s}" does not exist.')

        d = os.path.normpath(destination)
        if os.path.isfile(d):
            if not force:
                raise OSError(f'Destination "{d}" exists already.')

        if os.path.isdir(d):
            d = os.path.join(d, os.path.basename(s))

        assert s != d
        desc = description.format(s, d)
        debug(f"File_op(running once): {desc}.")
        op(s, d, **kwargs)


def _copy_op(source: str, destination: str, **kwargs: typing.Any) -> None:
    shutil.copyfile(source, destination, **kwargs)


def _recursive_copy_op(source: str, destination: str, **kwargs: typing.Any) -> None:
    if os.path.isdir(source):
        assert os.path.isdir(destination) or not os.path.exists(destination)
        copy_tree(source, destination)
    else:
        assert not os.path.isdir(destination)
        assert not os.path.exists(destination)
        shutil.copyfile(source, destination, **kwargs)


def copy(
    system_context: typing.Optional[SystemContext],
    *args: str,
    recursive: bool = False,
    **kwargs: typing.Any,
) -> None:
    """Copy files."""
    if recursive:
        return _file_op(
            system_context,
            _recursive_copy_op,
            'Copying "{}" to "{}" (recursive).',
            *args,
            **kwargs,
        )
    return _file_op(system_context, _copy_op, 'Copying "{}" to "{}".', *args, **kwargs)


def move(
    system_context: typing.Optional[SystemContext], *args: str, **kwargs: typing.Any
) -> None:
    """Move files."""
    return _file_op(
        system_context, shutil.move, 'Moving "{}" to "{}".', *args, **kwargs
    )


def remove(
    system_context: typing.Optional[SystemContext],
    *files: str,
    recursive: bool = False,
    force: bool = False,
    outside: bool = False,
) -> None:
    """Delete a file inside of a system."""
    sc = None if outside else system_context
    for file in expand_files(sc, *files, recursive=recursive):
        trace(f'Removing "{file}".')

        if not os.path.exists(file):
            if force:
                continue
            raise GenerateError(f'Failed to delete: "{file}" does not exist.')
        if os.path.isdir(file) and not os.path.islink(file):
            if recursive:
                shutil.rmtree(file)
            else:
                os.rmdir(file)
        else:
            try:
                os.unlink(file)
            except Exception:
                if not force:
                    raise
                else:
                    verbose(f'Failed to unlink "{file}".')
