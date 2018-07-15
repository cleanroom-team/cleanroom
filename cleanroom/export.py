#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CleanRoom functionality.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from .helper import disc
from .helper.run import run as helper_run
from .printer import (debug, fail, Printer, success, trace, verbose,)

import collections
import json
import os
import re
import shutil
import sys


ExportDataSet = collections.namedtuple('ExportDataSet', ['full_name', 'system', 'timestamp', 'mtime', 'sha'])


class Exporter:
    def __init__(self, repository):
        self._repository = repository
        self._export_data_sets = sorted(self._parse_borg_list(), key=lambda x: x.full_name)
        print('Exporter initialized')

    @staticmethod
    def _run_borg(*args, **kwargs):
        env = os.environ
        env['LC_ALL'] = 'C'
        env['LANG'] = 'en_US.UTF-8'
        result = helper_run('/usr/bin/borg', *args,
                            env=env, trace_output=trace, **kwargs)
        if result.returncode != 0:
            fail('Failed to retrieve data from borg.')

        return result

    def _parse_borg_list(self):
        trace('Running borg list on repository "{}".'.format(self._repository))
        result = Exporter._run_borg('list', self._repository)

        pattern = re.compile('(([a-zA-Z][a-zA-Z0-9_-]*)[_-]([0-9]+[\._-][0-9]+))\s+(.*) \\[([a-fA-F0-9]+)\\]')

        for line in result.stdout.splitlines():
            if not line:
                continue

            match = pattern.search(line)
            if match is None:
                fail('Failed to parse borg list output.')

            yield ExportDataSet(*match.groups())

    @staticmethod
    def _unique(seq, idfun=None):
        # order preserving
        if idfun is None:
           def idfun(x): return x
        seen = {}
        result = []
        for item in seq:
           marker = idfun(item)
           if marker in seen: continue
           seen[marker] = 1
           result.append(item)
        return result

    def systems(self):
        return Exporter._unique(self._export_data_sets, lambda x: x.system)

    def timestamps(self, system):
        return [ds for ds in self._export_data_sets if ds.system == system]

    def has_system_with_timestamp(self, system, timestamp):
        return [ds for ds in self._export_data_sets if ds.system == system and ds.timestamp == timestamp]

    def export(self, system, timestamp):
        assert [ds for ds in self._export_data_sets if ds.system == system and ds.timestamp == timestamp]
        return ExportContents(self._repository, system, timestamp)


File = collections.namedtuple('File', ['path', 'size', 'healthy', 'type'])


class ExportContents:
    def __init__(self, repository, system, timestamp):
        self._repository = repository
        self._system = system
        self._timestamp = timestamp
        self._contents = []

        result = Exporter._run_borg('list', '--json-lines', self._backup_name())
        for line in result.stdout.splitlines():
            json_data = json.loads(line)
            self._contents.append(File(json_data.get('path'), json_data.get('size'),
                                       json_data.get('healthy'), json_data.get('type')))

    def _backup_name(self):
            return '{}::{}-{}'.format(self._repository, self._system, self._timestamp)

    def _has_contents(self, path):
        return [f for f in self._contents if f.path == path]

    def kernel_name(self,):
        path = 'linux-{}.efi'.format(self._timestamp)
        assert self._has_contents(path)
        return path

    def root_name(self):
        path = 'root_{}'.format(self._timestamp)
        assert self._has_contents(path)
        return path

    def verity_name(self):
        path = 'vrty_{}'.format(self._timestamp)
        assert self._has_contents(path)
        return path

    def extract(self, path, *args, **kwargs):
        result = Exporter._run_borg('extract', *args, self._backup_name(), path, **kwargs)
        if result.returncode != 0:
            fail('Failed to extract "{}" from {}.'.format(path, self._backup_name()))
        return result.stdout

    def file(self, path):
        for f in self._contents:
            if f.path == path:
                return f
        return None
