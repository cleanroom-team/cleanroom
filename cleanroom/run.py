#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import subprocess


def run(ctx, *args):
    completed_process = subprocess.run(*args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    reportCompletedProcess(ctx.printer.trace, completed_process)
    return completed_process


def reportCompletedProcess(channel, completed_process):
    channel('Arguments  : {}'.format(' '.join(completed_process.args)))
    channel('Return Code: {}'.format(completed_process.returncode))
    channel('StdOut     : {}'.format(completed_process.stdout))
    channel('StdErr     : {}'.format(completed_process.stderr))


if __name__ == '__main__':
    pass
