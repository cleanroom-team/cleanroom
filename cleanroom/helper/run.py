# -*- coding: utf-8 -*-
"""Run external commands.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.exceptions import GenerateError
from cleanroom.printer import trace

import os
import subprocess
import typing


def _quote_args(*args: str) -> str:
    # FIXME: Do better quoting!
    return '"' + " ".join(args) + '"'


def report_completed_process(
    channel: typing.Optional[typing.Callable[..., None]],
    completed_process: subprocess.CompletedProcess,
) -> None:
    """Report the completion state of an external command."""
    if channel is None:
        return

    stdout: str = "<REDIRECTED>"
    stderr: str = stdout

    if completed_process.stdout is not None:
        stdout = completed_process.stdout

    if completed_process.stderr is not None:
        stderr = completed_process.stderr

    if completed_process.returncode != 0 or stdout or stderr:
        channel("Arguments  : {}".format(" ".join(completed_process.args)))
        channel(f"Return Code: {completed_process.returncode}")
        _report_output_lines(channel, "StdOut     :", stdout)
        _report_output_lines(channel, "StdErr     :", stderr)


def run(
    *args: str,
    returncode: typing.Optional[int] = 0,
    work_directory: typing.Optional[str] = None,
    trace_output: typing.Optional[typing.Callable[..., None]] = trace,
    chroot: typing.Optional[str] = None,
    shell: bool = False,
    stdout: typing.Optional[str] = None,
    stderr: typing.Optional[str] = None,
    chroot_helper: typing.Optional[str] = None,
    **kwargs: typing.Any,
) -> subprocess.CompletedProcess:
    """Run command and trace the external command result and output."""
    if work_directory is not None:
        os.chdir(work_directory)

    if shell:
        args = ("/usr/bin/bash", "-c", _quote_args(*args))
    if chroot is not None:
        assert chroot_helper
        args = (
            chroot_helper,
            f"--directory={chroot}",
            "--settings=no",
            "--uuid=36ba2dc69f9a49048afa3eab4063c44f",
            "--register=no",
            "--keep-unit",
            *args,
        )

    if trace_output:
        if work_directory:
            trace_output("Running", args, "in", work_directory)
        else:
            trace_output("Running", args)

    stdout_fd: typing.Optional[typing.TextIO] = None
    stderr_fd: typing.Optional[typing.TextIO] = None
    try:
        if stdout:
            if trace_output:
                trace_output(f">> Redirecting stdout to {stdout}.")
            stdout_fd = open(stdout, mode="w")

        if stderr:
            if trace_output:
                trace_output(f">> Redirecting stderr to {stderr}.")
            stderr_fd = open(stderr, mode="w")

        completed_process = subprocess.run(
            args,
            stdout=stdout_fd or subprocess.PIPE,
            stderr=stdout_fd or subprocess.PIPE,
            **kwargs,
        )
    except subprocess.TimeoutExpired as to:
        print(f"Timeout: STDOUT so far: {to.stdout!r}\nSTDERR so far:{to.stderr!r}\n.")
        raise

    finally:
        if stdout_fd:
            stdout_fd.close()
        if stderr_fd:
            stderr_fd.close()

    if not completed_process.stdout is str and not completed_process.stdout is None:
        completed_process.stdout = completed_process.stdout.decode("utf-8")
    if not completed_process.stderr is str and not completed_process.stderr is None:
        completed_process.stderr = completed_process.stderr.decode("utf-8")

    assert completed_process is not None

    report_completed_process(trace_output, completed_process)

    if returncode is not None and completed_process.returncode != returncode:
        raise GenerateError(
            f"Unexpected return value {completed_process.returncode} (expected {returncode})."
        )

    return completed_process


def _report_output_lines(
    channel: typing.Callable[..., None], headline: str, line_data: str
) -> None:
    """Pretty-print output lines."""
    if line_data:
        channel(headline)
        if line_data == "" or line_data == "\n":
            return
        lines = line_data.split("\n")
        for line in lines:
            channel(f"    {line}")
