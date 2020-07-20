# -*- coding: utf-8 -*-
"""_write_deploy_info command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.exceptions import GenerateError
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import json
import os
import typing


class WriteDeployInfoCommand(Command):
    """The _write_deploy_info command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_write_deploy_info",
            syntax="",
            help_string="Write deploy info file.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def register_substitutions(self) -> typing.List[typing.Tuple[str, str, str]]:
        return [
            ("DEPLOY_TYPE", "", "Type of deployment to use for the current system",),
            (
                "DEPLOY_TYPE_EXTRA_PARAMETERS",
                "",
                "Extra parameters to pass on to the deployment call",
            ),
            (
                "DEPLOY_EXTRA_SYSTEMS",
                "",
                "Space-separated list of extra systems to deploy in addition to the main system",
            ),
            (
                "DEPLOY_DEVICE_IDS",
                "",
                "Space-separated list of device ids that should be partitioned",
            ),
            (
                "DEPLOY_<DEVICE_ID>_REPART_D",
                "",
                "path (relative to this file) to the device_ids systemd-repart.d directory",
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
        extra_dir = os.path.join(system_context.boot_directory, "extra")
        os.makedirs(extra_dir, exist_ok=True)

        deployment_type = system_context.substitution_expanded("DEPLOY_TYPE", "")
        deployment_parameters: typing.List[str] = []
        if not deployment_type:
            image_device = system_context.substitution_expanded("IMAGE_DEVICE", "")
            if image_device:
                deployment_type = "image_partition"
                efi_partition = system_context.substitution_expanded(
                    "EFI_PARTITION_PARTUUID", ""
                )
                if not efi_partition:
                    raise GenerateError(
                        "No EFI_PARTITION_PARTUUID substitution defined when trying to write deploy.json",
                        location=location,
                    )
                image_fs = system_context.substitution_expanded("IMAGE_FS", "")
                assert image_fs
                image_options = system_context.substitution_expanded(
                    "IMAGE_OPTIONS", ""
                )
                if image_options:
                    image_options = "nodev,nosuid,noexec,{}".format(image_options)
                else:
                    image_options = "nodev,nosuid,noexec"
                deployment_parameters = [
                    "--efi-device=PARTUUID={}".format(efi_partition),
                    "--image-device={}".format(image_device),
                    "--image-fs-type={}".format(image_fs),
                    "--image-options={}".format(image_options),
                ]
                deployment_parameters += system_context.substitution_expanded(
                    "DEPLOY_TYPE_EXTRA_PARAMETERS", ""
                ).split()

        devices: typing.List[typing.Dict[str, str]] = []
        device_ids = system_context.substitution_expanded(
            "DEPLOY_DEVICE_IDS", ""
        ).split()

        for di in device_ids:
            assert di
            path = system_context.substitution_expanded(
                "DEPLOY_{}_REPART_D".format(di), ""
            )
            assert path

            devices.append({"device_id": di, "repart_d": path})

        data: typing.Dict[str, typing.Any] = {}
        data["version"] = 1
        data["type"] = deployment_type
        if deployment_parameters:
            data["parameters"] = deployment_parameters
        if devices:
            data["storage"] = devices
        extra_systems = system_context.substitution_expanded(
            "DEPLOY_EXTRA_SYSTEMS", ""
        ).split()
        if extra_systems:
            data["extra_systems"] = extra_systems

        deploy_file = os.path.join(extra_dir, "deploy.json")
        with open(deploy_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
