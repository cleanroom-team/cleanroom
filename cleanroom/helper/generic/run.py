#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run external commands.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.exceptions as ex

import os
import subprocess


def run(*args, exit_code=0, work_directory=None,
        trace_output=None, chroot=None, shell=False, **kwargs):
    """Run command and trace the external command result and output."""
    if work_directory is not None:
        os.chdir(work_directory)

    if shell:
        args = ('/usr/bin/bash', '-c', *args)
    if chroot is not None:
        args = ('/usr/bin/arch-chroot', chroot, *args)

    if trace_output is not None:
        if work_directory:
            trace_output('Running:', args, 'in', work_directory)
        else:
            trace_output('Running', args)

    completed_process = subprocess.run(args,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       **kwargs)
    completed_process.stdout = completed_process.stdout.decode('utf-8')
    completed_process.stderr = completed_process.stderr.decode('utf-8')

    report_completed_process(trace_output, completed_process)

    if exit_code is not None and completed_process.returncode != exit_code:
        raise ex.GenerateError('Unexpected return value {} (expected {}).'
                               .format(completed_process.returncode,
                                       exit_code))

    return completed_process


def report_completed_process(channel, completed_process):
    """Report the completion state of an external command."""
    if channel is None:
        return

    channel('Arguments  : {}'.format(' '.join(completed_process.args)))
    channel('Return Code: {}'.format(completed_process.returncode))
    channel('StdOut     :')
    _report_output_lines(channel, completed_process.stdout)
    channel('StdErr     :')
    _report_output_lines(channel, completed_process.stderr)


def _report_output_lines(channel, line_data):
    """Pretty-print output lines."""
    if line_data == '' or line_data == '\n':
        return
    lines = line_data.split('\n')
    for line in lines:
        channel('    {}'.format(line))


if __name__ == '__main__':
    pass
