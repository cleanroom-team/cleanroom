# -*- coding: utf-8 -*-
"""creato an image ready to be exported from clrm.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.helper.file import file_size
from cleanroom.helper.run import run
from cleanroom.printer import debug
from cleanroom.systemcontext import SystemContext

import os
import typing


def _write_repart_config(
    dir: str, file: str, *, type: str, image: str, label: str = "", uuid: str = ""
):
    with open(os.path.join(dir, file), "w") as conf:
        conf.write("[Partition]\n")
        conf.write(f"Type={type}\n")
        conf.write("SizeMinBytes=4096\n")
        conf.write(f"CopyBlocks={image}\n")
        if label:
            conf.write(f"Label={label}\n")
        if uuid:
            conf.write(f"UUID={uuid}\n")


class CreateExportImageCommand(Command):
    """The _create_export_image Command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_create_export_image",
            syntax="<IMAGE_FILE> "
            "efi_fsimage=<EFI_PARTITION_IMAGE> "
            "[efi_label=<STRING>] "
            "[efi_uuid=<UUID>] "
            "root_fsimage=<ROOT_PARTITION_IMAGE>] "
            "[root_label=<STRING>] "
            "root_uuid=<UUID> "
            "verity_fsimage=<VERITY_PARTITION_IMAGE>] "
            "[verity_label=<STRING>] "
            "verity_uuid=UUID",
            help_string="Create a filesystem image ready to be exported from clrm.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate arguments."""
        self._validate_args_exact(location, 1, "A image file name is needed.", *args)
        self._validate_kwargs(
            location,
            (
                "efi_fsimage",
                "efi_label",
                "efi_uuid",
                "root_fsimage",
                "root_label",
                "root_uuid",
                "verity_fsimage",
                "verity_label",
                "verity_uuid",
            ),
            **kwargs,
        )
        self._require_kwargs(
            location,
            (
                "efi_fsimage",
                "root_fsimage",
                "root_uuid",
                "verity_fsimage",
                "verity_uuid",
            ),
            **kwargs,
        )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        image_filename = args[0]

        efi_partition = kwargs.get("efi_fsimage", "")
        efi_label = kwargs.get("efi_label", "")
        efi_uuid = kwargs.get("efi_uuid", "")
        assert efi_partition

        root_partition = kwargs.get("root_fsimage", "")
        root_label = kwargs.get("root_label", "")
        root_uuid = kwargs.get("root_uuid", "")
        assert root_partition

        verity_partition = kwargs.get("verity_fsimage", "")
        verity_label = kwargs.get("verity_label", "")
        verity_uuid = kwargs.get("verity_uuid", "")
        assert verity_partition

        efi_size = file_size(None, efi_partition)
        root_size = file_size(None, root_partition)
        verity_size = file_size(None, verity_partition)
        total_size = (2 * 1024 * 1024) + efi_size + root_size + verity_size

        debug(
            f"Creating export image with {total_size} bytes (EFI: {efi_size}, root: {root_size}, verity: {verity_size})"
        )

        with open(image_filename, "wb") as fd:
            fd.seek(total_size - 1)
            fd.write(b"\0")

        repart_d_directory = os.path.join(system_context.cache_directory, "repart.d")
        os.makedirs(repart_d_directory)

        _write_repart_config(
            repart_d_directory,
            "10_efi.conf",
            type="esp",
            image=efi_partition,
            label=efi_label,
            uuid=efi_uuid,
        )
        _write_repart_config(
            repart_d_directory,
            "20_rootfs.conf",
            type="root-x86-64",
            image=root_partition,
            label=root_label,
            uuid=root_uuid,
        )
        _write_repart_config(
            repart_d_directory,
            "30_verity.conf",
            type="root-x86-64-verity",
            image=verity_partition,
            label=verity_label,
            uuid=verity_uuid,
        )

        run(
            self._binary(Binaries.SYSTEMD_REPART),
            "--dry-run=no",
            "--empty=require",
            f"--definitions={repart_d_directory}",
            image_filename,
        )
