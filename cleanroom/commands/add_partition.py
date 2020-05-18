# -*- coding: utf-8 -*-
"""add_partition command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.exceptions import ParseError
from cleanroom.helper.file import create_file, makedirs
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os.path
import typing


class AddPartitionCommand(Command):
    """The add_partition command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "add_partition",
            syntax="name type=<TYPE> [label=<LABEL> uuid=<UUID> priority=<INT> weight=<INT> "
            "paddingWeight=<INT> minSize=<SIZE> maxSize=<SIZE> "
            "minPadding=<SIZE> maxPadding=<SIZE>]",
            help_string="Add a partition to be created on the system by systemd-repart.\n",
            file=__file__,
            **services
        )

    def validate(self, location: Location, *args: str, **kwargs: typing.Any) -> None:
        """Validate the arguments."""
        self._validate_args_exact(
            location, 1, '"{}" needs a name for the partition file.', *args
        )
        self._validate_kwargs(
            location,
            (
                "type",
                "label",
                "uuid",
                "priority",
                "weight",
                "paddingWeight",
                "minSize",
                "maxSize",
                "minPadding",
                "maxPadding",
            ),
            **kwargs
        )
        self._require_kwargs(location, ("type",), **kwargs)
        type = kwargs.get("type")
        if not type in (
            "esp",
            "xbootldr",
            "swap",
            "home",
            "srv",
            "var",
            "tmp",
            "linux-generic",
            "root",
            "root-verity",
            "root-secondary",
            "root-secondary-verity",
            "root-x86",
            "root-x86-verity",
            "root-x86-64",
            "root-x86-64-verity",
            "root-arm",
            "root-arm-verity",
            "root-arm64",
            "root-arm64-verity",
            "root-ia64",
            "root-ia64-verity",
        ):
            raise ParseError("Invalid type found: {}.".format(type))

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: str,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        name = args[0]
        if not name.endswith(".conf"):
            name += ".conf"

        contents = "[Partition]\n"

        type = kwargs.get("type", "")
        contents += "Type={}\n".format(type)
        label = kwargs.get("label", "")
        if label:
            contents += "Label={}\n".format(label)
        uuid = kwargs.get("uuid", "")
        if uuid:
            contents += "UUID={}\n".format(uuid)
        priority = kwargs.get("priority", 0)
        if priority != 0:
            contents += "Priority={}\n".format(priority)
        weight = kwargs.get("weight", 1000)
        if weight != 1000:
            contents += "Weight={}\n".format(weight)
        padding_weight = kwargs.get("paddingWeight", 0)
        if padding_weight != 0:
            contents += "PaddingWeight={}\n".format(padding_weight)
        minSize = kwargs.get("minSize", "")
        if minSize:
            contents += "SizeMinBytes={}\n".format(minSize)
        maxSize = kwargs.get("maxSize", "")
        if maxSize:
            contents += "SizeMaxBytes={}\n".format(maxSize)
        minPadding = kwargs.get("minPadding", "")
        if minPadding:
            contents += "PaddingMinBytes={}\n".format(minPadding)
        maxPadding = kwargs.get("maxPadding", "")
        if maxPadding:
            contents += "PaddingMaxBytes={}\n".format(maxPadding)

        makedirs(system_context, "/usr/lib/repart.d", mode=0o750, exist_ok=True)
        create_file(
            system_context,
            os.path.join("/usr/lib/repart.d", name),
            contents.encode("utf-8"),
            mode=0o644,
        )
