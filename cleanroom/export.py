#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CleanRoom functionality.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from __future__ import annotations

from .helper.run import run
from .printer import fail, trace

import collections
import json
import os
import re
import subprocess
import typing


ExportDataSet = collections.namedtuple('ExportDataSet',
                                       ['full_name', 'system', 'timestamp',
                                        'mtime', 'sha'])


class Exporter:
    def __init__(self, repository: str) -> None:
        self._repository = repository
        self._export_data_sets = sorted(self._parse_borg_list(),
                                        key=lambda x: x.full_name)
        print('Exporter initialized')

    @staticmethod
    def run_borg(*args: str, **kwargs: typing.Any) \
            -> subprocess.CompletedProcess:
        env = os.environ
        env['LC_ALL'] = 'C'
        env['LANG'] = 'en_US.UTF-8'
        result = run('/usr/bin/borg', *args, env=env, trace_output=trace, **kwargs)
        if result.returncode != 0:
            fail('Failed to retrieve data from borg.')

        return result

    def _parse_borg_list(self) -> typing.Generator[ExportDataSet, None, None]:
        trace('Running borg list on repository "{}".'.format(self._repository))
        result = Exporter.run_borg('list', self._repository)

        pattern = re.compile(r'(([a-zA-Z][a-zA-Z0-9_-]*)[_-]'
                             '([0-9]+[._-][0-9]+))\\s+(.*) '
                             '\\[([a-fA-F0-9]+)\\]')

        for line in result.stdout.splitlines():
            if not line:
                continue

            match = pattern.search(line)
            if match is None:
                fail('Failed to parse borg list output.')
            else:
                yield ExportDataSet(*match.groups())

    @staticmethod
    def _unique(seq: typing.List[ExportDataSet],
                function: typing.Callable[[ExportDataSet], typing.Any] = lambda x: x) \
            -> typing.List[ExportDataSet]:
        # order preserving
        seen = set()  # type: typing.Set[typing.Any]
        result = []  # type: typing.List[ExportDataSet]
        for item in seq:
            marker = function(item)
            if marker in seen:
                continue
            seen.add(marker)
            result.append(item)
        return result

    def systems(self) -> typing.List[ExportDataSet]:
        return Exporter._unique(self._export_data_sets, lambda x: x.system)

    def timestamps(self, system: str) -> typing.List[ExportDataSet]:
        return [ds for ds in self._export_data_sets if ds.system == system]

    def has_system_with_timestamp(self, system: str, timestamp: str) -> typing.List[ExportDataSet]:
        return [ds for ds in self._export_data_sets if ds.system == system and ds.timestamp == timestamp]

    def export(self, system: str, timestamp: str) -> ExportContents:
        assert [ds for ds in self._export_data_sets if ds.system == system and ds.timestamp == timestamp]
        return ExportContents(self._repository, system, timestamp)


File = collections.namedtuple('File', ['path', 'size', 'healthy', 'type'])


class ExportContents:
    def __init__(self, repository: str, system: str, timestamp: str) -> None:
        self._repository = repository
        self._system = system
        self._timestamp = timestamp
        self._contents: typing.List[File] = []

        result = Exporter.run_borg('list', '--json-lines', self._backup_name())
        for line in result.stdout.splitlines():
            json_data = json.loads(line)
            self._contents.append(File(json_data.get('path'), json_data.get('size'),
                                       json_data.get('healthy'), json_data.get('type')))

    def _backup_name(self) -> str:
            return '{}::{}-{}'.format(self._repository, self._system, self._timestamp)

    def _has_contents(self, path: str) -> typing.List[File]:
        return [f for f in self._contents if f.path == path]

    def kernel_name(self) -> str:
        path = 'linux-{}.efi'.format(self._timestamp)
        assert self._has_contents(path)
        return path

    def root_name(self) -> str:
        path = 'root_{}'.format(self._timestamp)
        assert self._has_contents(path)
        return path

    def verity_name(self) -> str:
        path = 'vrty_{}'.format(self._timestamp)
        assert self._has_contents(path)
        return path

    def extract(self, path: str, *args: str, **kwargs: typing.Any) -> str:
        result = Exporter.run_borg('extract', *args, self._backup_name(), path, **kwargs)
        if result.returncode != 0:
            fail('Failed to extract "{}" from {}.'.format(path, self._backup_name()))
        return result.stdout

    def file(self, path: str) -> typing.Optional[File]:
        for f in self._contents:
            if f.path == path:
                return f
        return None
