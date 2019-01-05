# -*- coding: utf-8 -*-
"""Run external commands.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.exceptions import GenerateError

import os
import subprocess


def _quote_args(*args):
    # FIXME: Do better quoting!
    return '"' + ' '.join(args) + '"'


def run(*args, returncode=0, work_directory=None,
        trace_output=None, chroot=None, shell=False,
        stdout=None, stderr=None, chroot_helper=None,
        **kwargs):
    """Run command and trace the external command result and output."""
    if work_directory is not None:
        os.chdir(work_directory)

    if shell:
        args = ('/usr/bin/bash', '-c', _quote_args(*args))
    if chroot is not None:
        assert chroot_helper
        args = (chroot_helper, chroot, *args)

    if trace_output is not None:
        if work_directory:
            trace_output('Running', args, 'in', work_directory)
        else:
            trace_output('Running', args)

    stdoutFd = subprocess.PIPE
    stderrFd = subprocess.PIPE

    completed_process = None

    try:
        if stdout is not None:
            trace_output('>> Redirecting stdout to {}.'.format(stdout))
            stdoutFd = open(stdout, mode='w')

        if stderr is not None:
            trace_output('>> Redirecting stderr to {}.'.format(stdout))
            stderrFd = open(stderr, mode='w')

        completed_process = subprocess.run(args,
                                           stdout=stdoutFd, stderr=stderrFd,
                                           **kwargs)
    except subprocess.TimeoutExpired as to:
        print('Timeout: STDOUT so far: {}\nSTDERR so far:{}\n.'.format(to.stdout, to.stderr))
        raise

    finally:
        if stdout is not None:
            stdoutFd.close()
        if stderr is not None:
            stderrFd.close()

    assert completed_process is not None

    if completed_process.stdout is not None:
        completed_process.stdout = completed_process.stdout.decode('utf-8')
    if completed_process.stderr is not None:
        completed_process.stderr = completed_process.stderr.decode('utf-8')

    report_completed_process(trace_output, completed_process)

    if returncode is not None and completed_process.returncode != returncode:
        raise GenerateError('Unexpected return value {} (expected {}).'
                            .format(completed_process.returncode, returncode))

    return completed_process


def report_completed_process(channel, completed_process):
    """Report the completion state of an external command."""
    if channel is None:
        return

    stdout = '<REDIRECTED>'
    stderr = stdout

    if completed_process.stdout is not None:
        stdout = completed_process.stdout

    if completed_process.stderr is not None:
        stderr = completed_process.stderr

    channel('Arguments  : {}'.format(' '.join(completed_process.args)))
    channel('Return Code: {}'.format(completed_process.returncode))
    _report_output_lines(channel, 'StdOut     :', stdout)
    _report_output_lines(channel, 'StdErr     :', stderr)


def _report_output_lines(channel, headline, line_data):
    """Pretty-print output lines."""
    channel(headline)
    if line_data == '' or line_data == '\n':
        return
    lines = line_data.split('\n')
    for line in lines:
        channel('    {}'.format(line))
