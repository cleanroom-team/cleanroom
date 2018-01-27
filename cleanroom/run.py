#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run external commands.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import subprocess


def run(ctx, *args):
    """Run command and trace the external command result and output."""
    completed_process = subprocess.run(*args,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
    report_completed_process(ctx.printer.trace, completed_process)
    return completed_process


def report_completed_process(channel, completed_process):
    """Report the completion state of an external command."""
    channel('Arguments  : {}'.format(' '.join(completed_process.args)))
    channel('Return Code: {}'.format(completed_process.returncode))
    channel('StdOut     : {}'.format(completed_process.stdout))
    channel('StdErr     : {}'.format(completed_process.stderr))


if __name__ == '__main__':
    pass
