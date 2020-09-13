# -*- coding: utf-8 -*-
"""_create_dmverity_fsimage command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.helper.file import size_extend
from cleanroom.helper.run import run
from cleanroom.systemcontext import SystemContext


import typing


class CreateDmverityFsimageCommand(Command):
    """The _create_dmverity_fsimage Command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_create_dmverity_fsimage",
            syntax="DMVERITY_IMAGE FILE " "[base_image=<BASE_FILE_IMAGE]",
            help_string="Export a filesystem image.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate arguments."""
        self._validate_args_exact(
            location, 1, "{} needs a filename for the dm-verity image.", *args
        )
        self._validate_kwargs(location, ("base_image",), **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        verity_file = args[0]
        base_image = kwargs.get("base_image", "")
        assert base_image

        result = run(
            self._binary(Binaries.VERITYSETUP), "format", base_image, verity_file
        )

        size_extend(verity_file)

        root_hash: typing.Optional[str] = None
        uuid: typing.Optional[str] = None
        for line in result.stdout.split("\n"):
            if line.startswith("Root hash:"):
                root_hash = line[10:].strip()
            if line.startswith("UUID:"):
                uuid = line[10:].strip()

        assert root_hash is not None
        assert uuid is not None

        system_context.set_substitution("LAST_DMVERITY_UUID", uuid)
        system_context.set_substitution("LAST_DMVERITY_ROOTHASH", root_hash)
