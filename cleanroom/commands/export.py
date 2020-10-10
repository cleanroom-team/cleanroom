# -*- coding: utf-8 -*-
"""export a system command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.exceptions import GenerateError, ParseError
from cleanroom.location import Location
from cleanroom.helper.file import exists, file_size
from cleanroom.helper.run import run
from cleanroom.systemcontext import SystemContext
from cleanroom.printer import debug, h2, info, trace, verbose


import os
import typing


def _setup_kernel_commandline(base_cmdline: str, root_hash: str) -> str:
    cmdline = " ".join(
        (
            base_cmdline,
            "root=/dev/mapper/root",
            "FOO",  # One of my mainboards eats the last letter of the last argument:-/
        )
    )
    return cmdline


def _validate_installation(location: Location, system_context: SystemContext) -> None:
    hostname = system_context.substitution_expanded("HOSTNAME")
    if not hostname:
        raise GenerateError(
            "Trying to export a system without a hostname.", location=location
        )

    machine_id = system_context.substitution_expanded("MACHINE_ID")
    if not machine_id:
        raise GenerateError(
            "Trying to export a system without " "a machine_id.", location=location
        )


def _uuid_ify(data: str) -> str:
    assert len(data) == 32
    return f"{data[0:8]}-{data[8:12]}-{data[12:16]}-{data[16:20]}-{data[20:]}"


class ExportCommand(Command):
    """The export_squashfs Command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "export",
            syntax="REPOSITORY "
            "[efi_key=<KEY>] [efi_cert=<CERT>] "
            "[efi_emulator=/path/to/Clover] "
            "[repository_compression=zstd] "
            "[repository_compression_level=5] "
            "[skip_validation=False] "
            "[usr_only=True]",
            help_string="Export a filesystem image.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate arguments."""
        self._validate_args_exact(
            location, 1, "{} needs a repository to export into.", *args
        )
        self._validate_kwargs(
            location,
            (
                "efi_key",
                "efi_cert",
                "efi_emulator",
                "repository_compression",
                "repository_compression_level",
                "skip_validation",
                "usr_only",
            ),
            **kwargs,
        )

        if "key" in kwargs:
            if "cert" not in kwargs:
                raise ParseError(
                    '"{}": cert keyword is required when ' "key keyword is given.",
                    location=location,
                )
        else:
            if "cert" in kwargs:
                raise ParseError(
                    '"{}": key keyword is required when ' "cert keyword is given.",
                    location=location,
                )

        repo_compression = kwargs.get("repository_compression", "zstd")
        if repo_compression not in (
            "none",
            "lz4",
            "zstd",
            "zlib",
            "lzma",
        ):
            raise ParseError(
                f'"{repo_compression}" is not a supported repository compression format.',
                location=location,
            )

        efi_emulator = kwargs.get("efi_emulator", "")
        if efi_emulator:
            if not os.path.isdir(os.path.join(efi_emulator, "EFI")):
                raise ParseError(
                    f'"{efi_emulator}" is not a valid efi emulator. The folder needs to contain a "EFI" folder.',
                    location=location,
                )
            if not os.path.isdir(os.path.join(efi_emulator, "Bootloaders")):
                raise ParseError(
                    f'"{efi_emulator}" is not a valid efi emulator. The folder needs to contain a "Bootloaders" folder.',
                    location=location,
                )
            if not os.path.isdir(os.path.join(efi_emulator, "BootSectors")):
                raise ParseError(
                    f'"{efi_emulator}" is not a valid efi emulator. The folder needs to contain a "BootSectors" folder.',
                    location=location,
                )

    def register_substitutions(self) -> typing.List[typing.Tuple[str, str, str]]:
        return [
            (
                "EXPORT_DIRECTORY",
                "",
                "The directory to export into. Only set while export command is running",
            ),
            (
                "ROOTFS_PARTLABEL",
                "${DISTRO_ID}_${DISTRO_VERSION_ID}",
                "Root filesystem partition label.",
            ),
            (
                "VRTYFS_PARTLABEL",
                "vrty_${DISTRO_VERSION_ID}",
                "Dm-verity filesystem partition label.",
            ),
            (
                "KERNEL_FILENAME",
                "${PRETTY_SYSTEM_NAME}_${DISTRO_VERSION_ID}.efi",
                "File name for the clrm image file",
            ),
            (
                "CLRM_IMAGE_FILENAME",
                "${PRETTY_SYSTEM_NAME}_${DISTRO_VERSION_ID}.img",
                "File name for the clrm image file",
            ),
            (
                "INITRD_GENERATOR",
                "mkinitcpio",
                "Initrd generator to use (default: mkinitcpio)",
            ),
        ]

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        cert = kwargs.get("efi_cert", "")
        efi_emulator = kwargs.get("efi_emulator", "")
        key = kwargs.get("efi_key", "")
        skip_validation = kwargs.get("skip_validation", False)
        repository = args[0]
        repository_compression = kwargs.get("repository_compression", "zstd")
        repository_compression_level = kwargs.get("repository_compression_level", 5)
        usr_only = kwargs.get("usr_only", True)

        h2(f'Exporting system "{system_context.system_name}".')
        debug("Running Hooks.")
        self._run_all_exportcommand_hooks(system_context)

        verbose("Preparing system for export.")
        self._execute(location.next_line(), system_context, "_write_deploy_info")

        # Create some extra data:
        self._create_root_tarball(location, system_context)

        root_partition = self._create_root_fsimage(
            location, system_context, usr_only=usr_only
        )
        assert root_partition
        (verity_partition, root_hash) = self._create_rootverity_fsimage(
            location,
            system_context,
            rootfs=root_partition,
        )
        assert root_hash

        has_kernel = os.path.exists(
            os.path.join(system_context.boot_directory, "vmlinuz")
        )
        if has_kernel:
            self._create_clrm_config_initrd(location, system_context, root_hash)
            self._create_initrd(location, system_context)

        cmdline = system_context.set_or_append_substitution(
            "KERNEL_CMDLINE", "systemd.volatile=true rootfstype=squashfs"
        )
        cmdline = _setup_kernel_commandline(cmdline, root_hash)

        kernel_file = ""
        if has_kernel:
            trace(
                f'KERNEL_FILENAME: {system_context.substitution("KERNEL_FILENAME", "")}'
            )
            kernel_file = os.path.join(
                system_context.boot_directory,
                system_context.substitution_expanded("KERNEL_FILENAME", ""),
            )

            assert kernel_file
            self._create_complete_kernel(
                location,
                system_context,
                cmdline,
                kernel_file=kernel_file,
                efi_key=key,
                efi_cert=cert,
            )

        efi_partition = os.path.join(
            system_context.cache_directory, "efi_partition.img"
        )

        self._create_efi_partition(
            location,
            system_context,
            efi_partition=efi_partition,
            kernel_file=kernel_file,
            efi_emulator=efi_emulator,
            root_hash=root_hash,
        )

        info("Validating installation for export.")
        if not skip_validation:
            _validate_installation(location.next_line(), system_context)

        export_directory = self.create_export_directory(system_context)
        assert export_directory
        self.create_image(
            location,
            system_context,
            export_directory,
            efi_partition=efi_partition,
            root_partition=root_partition,
            verity_partition=verity_partition,
            root_hash=root_hash,
        )

        system_context.set_substitution("EXPORT_DIRECTORY", export_directory)

        verbose(f"Exporting all data in {export_directory}.")
        self._execute(
            location.next_line(),
            system_context,
            "_export_directory",
            export_directory,
            compression=repository_compression,
            compression_level=repository_compression_level,
            repository=repository,
        )

        info("Cleaning up export location.")
        self.delete_export_directory(export_directory)
        system_context.set_substitution("EXPORT_DIRECTORY", "")

    def _create_root_tarball(
        self, location: Location, system_context: SystemContext
    ) -> None:
        tarball = "usr/lib/boot/root-fs.tar"
        os.makedirs(system_context.file_name("/usr/lib/boot"))

        if exists(system_context, tarball):
            raise GenerateError(
                f'"{self.name}": Root tarball "{tarball}" already exists.',
                location=location,
            )
        run(
            self._binary(Binaries.TAR),
            "-cf",
            tarball,
            "--sort=name",
            "etc",
            "root",
            work_directory=system_context.fs_directory,
        )

    def _create_complete_kernel(
        self,
        location: Location,
        system_context: SystemContext,
        cmdline: str,
        *,
        kernel_file: str,
        efi_key: str,
        efi_cert: str,
    ):
        self._create_efi_kernel(
            location,
            system_context,
            cmdline,
            kernel_file=kernel_file,
        )

        if efi_key and efi_cert:
            debug("Signing EFI kernel.")
            location.set_description("Sign EFI kernel")
            self._execute(
                location.next_line(),
                system_context,
                "sign_efi_binary",
                kernel_file,
                key=efi_key,
                cert=efi_cert,
                outside=True,
                keep_unsigned=False,
            )

        trace(f"Validating existence of {kernel_file}.")
        assert os.path.isfile(kernel_file)

    def _create_efi_partition(
        self,
        location: Location,
        system_context: SystemContext,
        *,
        efi_partition: str,
        efi_emulator: str,
        kernel_file: str,
        root_hash: str,
    ):
        extra_dir = os.path.join(system_context.boot_directory, "extra")
        extra_files = extra_dir if os.path.isdir(extra_dir) else ""

        self._execute(
            location,
            system_context,
            "_create_efi_fsimage",
            efi_partition,
            kernel_file=kernel_file,
            root_hash=root_hash,
            systemd_boot_loader=os.path.join(
                system_context.fs_directory,
                "usr/lib/systemd/boot/efi/systemd-bootx64.efi",
            ),
            extra_files=extra_files,
            efi_emulator=efi_emulator,
            partition_label="ESP",
        )

    def _create_root_fsimage(
        self, location: Location, system_context: SystemContext, *, usr_only: bool
    ) -> str:
        rootfs_label = system_context.substitution_expanded("ROOTFS_PARTLABEL", "")
        if not rootfs_label:
            raise GenerateError("ROOTFS_PARTLABEL is unset.")
        squashfs_file = os.path.join(
            system_context.cache_directory,
            rootfs_label,
        )

        self._execute(
            location,
            system_context,
            "_create_root_fsimage",
            squashfs_file,
            usr_only=usr_only,
        )

        return squashfs_file

    def _create_rootverity_fsimage(
        self, location: Location, system_context: SystemContext, *, rootfs: str
    ) -> typing.Tuple[str, str]:
        vrty_label = system_context.substitution_expanded("VRTYFS_PARTLABEL", "")
        if not vrty_label:
            raise GenerateError("VRTYFS_PARTLABEL is unset.")
        verity_file = os.path.join(system_context.cache_directory, vrty_label)

        self._execute(
            location,
            system_context,
            "_create_dmverity_fsimage",
            verity_file,
            base_image=rootfs,
        )
        root_hash = system_context.substitution("LAST_DMVERITY_ROOTHASH", "")
        assert root_hash

        return (verity_file, root_hash)

    def create_export_directory(self, system_context: SystemContext) -> str:
        """Return the root directory."""
        export_volume = os.path.join(system_context.scratch_directory, "export")
        btrfs_helper = self._service("btrfs_helper")
        if btrfs_helper.is_subvolume(export_volume):
            btrfs_helper.delete_subvolume_recursive(export_volume)
        btrfs_helper.create_subvolume(export_volume)

        return export_volume

    def create_image(
        self,
        location: Location,
        system_context: SystemContext,
        export_volume: str,
        *,
        efi_partition: str,
        root_partition: str,
        verity_partition: str,
        root_hash: str,
    ):
        image_name = system_context.substitution_expanded("CLRM_IMAGE_FILENAME", "")
        assert image_name

        image_filename = os.path.join(
            export_volume,
            image_name,
        )

        assert efi_partition
        assert root_partition
        assert verity_partition

        total_size = (
            (2 * 1024 * 1024)
            + file_size(None, efi_partition)
            + file_size(None, root_partition)
            + file_size(None, verity_partition)
        )

        root_uuid = _uuid_ify(root_hash[:32]) if root_hash else ""
        verity_uuid = _uuid_ify(root_hash[32:]) if root_hash else ""

        with open(image_filename, "wb") as fd:
            fd.seek(total_size - 1)
            fd.write(b"\b")

        self._execute(
            location,
            system_context,
            "_create_export_image",
            image_filename,
            efi_fsimage=efi_partition,
            efi_label="ESP",
            root_fsimage=root_partition,
            root_label=system_context.substitution_expanded("ROOTFS_PARTLABEL", ""),
            root_uuid=root_uuid,
            verity_fsimage=verity_partition,
            verity_label=system_context.substitution_expanded("VRTYFS_PARTLABEL", ""),
            verity_uuid=verity_uuid,
        )

    def delete_export_directory(self, export_directory: str) -> None:
        """Nothing to see, move on."""
        self._service("btrfs_helper").delete_subvolume(export_directory)

    def _create_efi_kernel(
        self,
        location: Location,
        system_context: SystemContext,
        cmdline: str,
        *,
        kernel_file: str,
    ) -> None:
        location.set_description("Create EFI kernel")
        self._execute(
            location.next_line(),
            system_context,
            "_create_efi_kernel",
            kernel_file,
            kernel=os.path.join(system_context.boot_directory, "vmlinuz"),
            initrd_directory=system_context.initrd_parts_directory,
            commandline=cmdline,
        )

    def _create_initrd(self, location: Location, system_context: SystemContext):
        location.set_description("Create initrd")
        initrd_parts = system_context.initrd_parts_directory
        os.makedirs(initrd_parts, exist_ok=True)

        initrd_generator = system_context.substitution_expanded(
            "INITRD_GENERATOR", "mkinitcpio"
        )
        assert initrd_generator

        self._execute(
            location.next_line(),
            system_context,
            f"_create_initrd_{initrd_generator}",
            os.path.join(initrd_parts, f"50-{initrd_generator}"),
        )

        assert os.path.exists(
            os.path.join(
                system_context.initrd_parts_directory, f"50-{initrd_generator}"
            )
        )

    def _create_clrm_config_initrd(
        self,
        location: Location,
        system_context: SystemContext,
        root_hash: str,
    ):
        location.set_description("Create clrm config initrd")
        os.makedirs(system_context.initrd_parts_directory, exist_ok=True)
        self._execute(
            location.next_line(),
            system_context,
            "_create_clrm_config_initrd",
            os.path.join(system_context.initrd_parts_directory, "99-clrm"),
            root_hash=root_hash,
        )

        assert os.path.exists(
            os.path.join(system_context.initrd_parts_directory, "99-clrm")
        )

    def _run_all_exportcommand_hooks(self, system_context: SystemContext) -> None:
        self._run_hooks(system_context, "_teardown")
        self._run_hooks(system_context, "export")

        # Now do tests!
        self._run_hooks(system_context, "testing")
