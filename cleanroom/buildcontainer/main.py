#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CleanRoom functionality.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from argparse import ArgumentParser, REMAINDER
import os
import subprocess
import sys
import typing


def _parse_commandline(*arguments: str) -> typing.Any:
    """Parse the command line options."""
    parser = ArgumentParser(
        description="Cleanroom OS build container runner", prog=arguments[0]
    )

    parser.add_argument(
        "--build-container",
        dest="build_container",
        action="store",
        required=True,
        help="The container to run the build in",
    )

    parser.add_argument(
        "--systems-directory",
        dest="systems_directory",
        action="store",
        required=True,
        help="Directory containing system definitions",
    )
    parser.add_argument(
        "--work-directory",
        dest="work_directory",
        action="store",
        required=True,
        help="Work area to create files in",
    )
    parser.add_argument(
        "--repository-base-directory",
        dest="repository_base_directory",
        action="store",
        required=True,
        help="The directory containing image repositories.",
    )
    parser.add_argument(
        "--bind",
        dest="bind",
        action="append",
        help="Extra paths to bind-mount into the container.",
    )
    parser.add_argument(
        "--bind-ro",
        dest="bind_ro",
        action="append",
        help="Extra paths to bind-mount into the container (read-only).",
    )
    parser.add_argument(
        "--with-network",
        dest="with_network",
        action="store_true",
        default=False,
        help="Keep network functional in the container.",
    )
    parser.add_argument(
        "--non-ephemeral",
        dest="non_ephemeral",
        action="store_true",
        default=False,
        help="Use a non-ephemeral container.",
    )

    parser.add_argument(
        dest="executable", help="The program to run", choices=["clrm", "bash"],
    )
    parser.add_argument(
        dest="args", nargs=REMAINDER, help="Arguments for the program to run",
    )

    parse_result = parser.parse_args(arguments[1:])

    return parse_result


def _validate_build_container(build_container: str) -> bool:
    if not os.path.isdir(os.path.join(build_container, "usr")):
        print(f"ERROR: {build_container} does not seem to contain an OS image")
        return False
    return True


def _find_python(build_container: str) -> str:
    for python in ["usr/bin/python3", "usr/bin/python"]:
        if os.path.join(build_container, python):
            return f"/{python}"

    print(f"ERROR: {build_container} does not contain a python interpreter")
    return ""


def create_container_dir(dir: str):
    if not os.path.isdir(dir):
        os.makedirs(dir)


def run() -> None:
    """Run cleanroom with command line arguments."""
    current_directory = os.getcwd()

    try:
        main(*sys.argv)
    finally:
        os.chdir(current_directory)


def main(*command_arguments: str) -> None:
    """Run cleanroom with arguments."""
    args = _parse_commandline(*command_arguments)

    build_container = os.path.realpath(args.build_container)

    if not _validate_build_container(build_container):
        sys.exit(1)

    python = _find_python(build_container)
    if not python:
        sys.exit(2)

    systems_directory = os.path.realpath(args.systems_directory)
    if not os.path.isdir(systems_directory):
        print(f"ERROR: systems directory {systems_directory} is not a directory.")
        sys.exit(3)
    work_directory = os.path.realpath(args.work_directory)
    if not os.path.isdir(work_directory):
        print(f"ERROR: work directory {work_directory} is not a directory.")
        sys.exit(3)
    repository_base_directory = os.path.realpath(args.repository_base_directory)
    if not os.path.isdir(repository_base_directory):
        print(
            f"ERROR: repository base directory {repository_base_directory} is not a directory."
        )
        sys.exit(3)

    code_directory = os.path.realpath(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    )

    # print(f'build chroot             : "{build_container}".')
    # print(f'    python executable    : "{python}".')
    # print(f'systems directory        : "{systems_directory}".')
    # print(f'work directory           : "{work_directory}".')
    # print(f'repository base directory: "{repository_base_directory}".')
    # print(f'code directory           : "{code_directory}.')

    extra_args: typing.List[str] = []
    if "BORG_BASE_DIR" in os.environ:
        borg_base_dir = os.environ["BORG_BASE_DIR"]
        if borg_base_dir:
            extra_args += [
                f"--bind={borg_base_dir}:/clrm/borg_base",
                "--setenv=BORG_BASE_DIR=/clrm/borg_base",
            ]
    if "BORG_PASSPHRASE" in os.environ:
        borg_passphrase = os.environ["BORG_PASSPHRASE"]
        if borg_passphrase:
            extra_args += [f"--setenv=BORG_PASSPHRASE={borg_passphrase}"]

    if args.bind:
        extra_args += [f"--bind={b}" for b in args.bind]
    if args.bind_ro:
        extra_args += [f"--bind-ro={b}" for b in args.bind_ro]

    run_args: typing.List[str] = []
    if args.executable == "bash":
        run_args = ["/usr/bin/bash", *args.args]
    else:
        run_args = [
            python,
            "/clrm/python/clrm",
            "--systems-directory=/clrm/systems",
            "--work-directory=/clrm/work",
            "--repository-base-directory=/clrm/repository",
            *args.args,
        ]

    if not args.with_network:
        extra_args += ["--private-network"]
    if not args.non_ephemeral:
        extra_args += ["--ephemeral"]

    result = subprocess.run(
        [
            "/usr/bin/systemd-nspawn",
            f"--directory={build_container}",
            "--setenv=PYTHONPATH=/clrm/python",
            "--bind-ro=/mnt/pkgs",
            f"--bind-ro={code_directory}:/clrm/python",
            f"--bind={work_directory}:/clrm/work_dir",
            f"--bind={repository_base_directory}:/clrm/repository",
            f"--bind-ro={systems_directory}:/clrm/systems",
            "--register=false",
            *extra_args,
            *run_args,
        ]
    )
    if result.returncode != 0:
        print(f"ERROR: CLRM failed with exit code {result.returncode}.")
    sys.exit(result.returncode)
