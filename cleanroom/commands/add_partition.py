# -*- coding: utf-8 -*-
"""add_partition command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.exceptions import ParseError
from cleanroom.location import Location
from cleanroom.printer import trace
from cleanroom.systemcontext import SystemContext

import os
import typing


class AddPartitionCommand(Command):
    """The add_partition command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "add_partition",
            syntax="name device=<device_id> type=<TYPE> [label=<LABEL> uuid=<UUID> priority=<INT> weight=<INT> "
            "paddingWeight=<INT> minSize=<SIZE> maxSize=<SIZE> "
            "minPadding=<SIZE> maxPadding=<SIZE>]",
            help_string="Add a partition to be created on the system.\n",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_args_exact(
            location, 1, '"{}" needs a name for the partition file.', *args
        )
        self._validate_kwargs(
            location,
            (
                "type",
                "device",
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

    def register_substitutions(self) -> typing.List[typing.Tuple[str, str, str]]:
        return [
            (
                "EFI_PARTITION_UUID",
                "",
                "The partition UUID of the first defined EFI partition",
            ),
        ]

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        name = args[0]
        if not name.endswith(".conf"):
            name += ".conf"

        device_id = kwargs.get("device", "disk0")
        assert not " " in device_id

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

        rel_path = os.path.join(
            system_context.substitution("DISTRO_ID"), "repart.d", device_id,
        )
        path = os.path.join(system_context.boot_directory, "extra", rel_path,)
        filename = os.path.join(path, name)
        trace("Creating repart.d file {} (relative: {}).".format(filename, rel_path))

        os.makedirs(path, mode=0o750, exist_ok=True)
        with open(filename, "wb") as f:
            f.write(contents.encode("utf-8"))
        os.chown(filename, 0, 0, follow_symlinks=False)
        os.chmod(filename, 0o644)

        # set up substitutions:
        device_ids = system_context.substitution_expanded(
            "DEPLOY_DEVICE_IDS", ""
        ).split()
        if not device_id in device_ids:
            device_ids.append(device_id)
        system_context.set_substitution("DEPLOY_DEVICE_IDS", " ".join(device_ids))

        key = "DEPLOY_{}_REPART_D".format(device_id)
        repart_path = system_context.substitution_expanded(key, "")
        if not repart_path:
            trace("Setting {} to {}.".format(key, rel_path))
            system_context.set_substitution(key, rel_path)
        else:
            assert rel_path == repart_path

        if type == "esp" and uuid:
            system_context.set_substitution("EFI_PARTITION_PARTUUID", uuid)
