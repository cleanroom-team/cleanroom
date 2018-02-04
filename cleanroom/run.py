#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run external commands.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.exceptions as ex

import os
import subprocess


def run(ctx, *args, exit_code=0, work_directory=None):
    """Run command and trace the external command result and output."""
    if work_directory:
        old_work_directory = os.getcwd()
        os.chdir(work_directory)

    completed_process = subprocess.run(*args,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
    if work_directory:
        os.chdir(old_work_directory)
    report_completed_process(ctx.printer.trace, completed_process)

    if exit_code is not None and completed_process.returncode != exit_code:
        raise ex.GenerateError('Unexpected return value {} (expected {}).'
                               .format(completed_process.returncode,
                                       exit_code))

    return completed_process


def report_completed_process(channel, completed_process):
    """Report the completion state of an external command."""
    channel('Arguments  : {}'.format(' '.join(completed_process.args)))
    channel('Return Code: {}'.format(completed_process.returncode))
    channel('StdOut     : {}'.format(completed_process.stdout))
    channel('StdErr     : {}'.format(completed_process.stderr))


if __name__ == '__main__':
    pass
