# -*- coding: utf-8 -*-
"""create_initrd command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.helper.file import copy, create_file, remove, move
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext
from cleanroom.printer import info, trace

import os
import textwrap
import typing


def _device_ify(device: str) -> str:
    if not device:
        return ""
    if device.startswith("PARTLABEL="):
        device = "/dev/disk/by-partlabel/" + device[10:]
    elif device.startswith("LABEL="):
        device = "/dev/disk/by-label/" + device[6:]
    elif device.startswith("PARTUUID="):
        device = "/dev/disk/by-partuuid/" + device[9:]
    elif device.startswith("UUID="):
        device = "/dev/disk/by-uuid/" + device[5:]
    elif device.startswith("ID="):
        device = "/dev/disk/by-id/" + device[3:]
    elif device.startswith("PATH="):
        device = "/dev/disk/by-path/" + device[5:]
    assert device.startswith("/dev/")
    return device


def _escape_device(device: str) -> str:
    device = _device_ify(device)

    device = device.replace("-", "\\x2d")
    device = device.replace("=", "\\x3d")
    device = device.replace(";", "\\x3b")
    device = device.replace("/", "-")

    return device[1:]


def _create_install_hook(
    location: Location, system_context: SystemContext, name: str, contents: str
) -> str:
    location.set_description("install mkinitcpio install hook {}".format(name))
    path = os.path.join("/usr/lib/initcpio/install", name)
    create_file(system_context, path, contents.encode("utf-8"))
    return path


def _cleanup_extra_files(
    location: Location, system_context: SystemContext, *files: str
) -> None:
    location.set_description("Remove extra mkinitcpio files")


class CreateInitrdCommand(Command):
    """The create_initrd command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "create_initrd",
            syntax="<INITRD_FILE>",
            help_string="Create an initrd.",
            file=__file__,
            **services
        )

        self._vg: typing.Optional[str] = None
        self._image_fs: typing.Optional[str] = None
        self._image_device: typing.Optional[str] = None
        self._image_options: typing.Optional[str] = None

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_arguments_exact(
            location, 1, '"{}" takes an initrd to create.', *args, **kwargs
        )

    def _create_systemd_units(
        self, location: Location, system_context: SystemContext
    ) -> typing.Sequence[str]:
        location.set_description("Install extra systemd units")
        to_clean_up = [
            "/usr/lib/systemd/system/initrd-sysroot-setup.service",
            "/usr/lib/systemd/system/initrd-find-root-lv-partitions.service",
            "/usr/lib/systemd/system/images.mount",
            "/usr/lib/systemd/system/initrd-find-image-partitions.service",
        ]

        create_file(
            system_context,
            "/usr/lib/systemd/system/initrd-sysroot-setup.service",
            textwrap.dedent(
                """\
                    [Unit]
                    Description=Set up root fs in /sysroot
                    DefaultDependencies=no
                    ConditionPathExists=/sysroot/usr/lib/boot/root-fs.tar
                    Requires=sysroot.mount
                    After=sysroot.mount systemd-volatile-root.service
                    Before=initrd-root-fs.target shutdown.target
                    Conflicts=shutdown.target
                    AssertPathExists=/etc/initrd-release
                    
                    [Service]
                    Type=oneshot
                    RemainAfterExit=yes
                    ExecStart=/usr/bin/tar -C /sysroot -xf /sysroot/usr/lib/boot/root-fs.tar
                    """
            ).encode("utf-8"),
            mode=0o644,
        )
        trace("Wrote initrd-sysroot-setup.service")

        if self._vg is not None:
            device_name = "dev-{}-{}".format(self._vg, self._full_name)
            create_file(
                system_context,
                "/usr/lib/systemd/system/initrd-find-root-lv-partitions.service",
                textwrap.dedent(
                    """\
                        [Unit]
                        Description=Find partitions in root LV
                        DefaultDependencies=no
                        ConditionPathExists=/dev/{1}/{2}
                        After={0}.device
                        BindsTo={0}.device
                        Requisite={0}.device
                        
                        [Service]
                        WorkingDirectory=/
                        Type=oneshot
                        RemainAfterExit=yes
                        ExecStart=/usr/bin/partprobe /dev/{1}/{2}
                        
                        [Install]
                        WantedBy={0}.device
                        """
                )
                .format(device_name, self._vg, self._full_name)
                .encode("utf-8"),
                mode=0o644,
            )
            trace("Wrote initrd-find-root-lv-partitions.service")

        if self._image_device:
            create_file(
                system_context,
                "/usr/lib/systemd/system/images.mount",
                textwrap.dedent(
                    """\
                        [Unit]
                        Description=Mount /images in initrd
                        DefaultDependencies=no
                        After=systemd-cryptsetup@main.service
                        
                        [Mount]
                        What={}
                        Where=/images
                        Type={}
                        Options={},nodev,noexec,nosuid,ro
                        """
                )
                .format(self._image_device, self._image_fs, self._image_options)
                .encode("utf-8"),
                mode=0o644,
            )
            trace(
                "Wrote images.mount (Where={}, Type={}, Options={})".format(
                    self._image_device, self._image_fs, self._image_options
                )
            )

            create_file(
                system_context,
                "/usr/lib/systemd/system/initrd-find-image-partitions.service",
                textwrap.dedent(
                    """\
                        [Unit]
                        Description=Find partitions in image files
                        DefaultDependencies=no
                        ConditionFileNotEmpty=/images/{0}
                        After=images.mount
                        BindsTo=images.mount
                        Requisite=images.mount
                        
                        [Service]
                        WorkingDirectory=/
                        Type=oneshot
                        RemainAfterExit=yes
                        ExecStart=/usr/bin/losetup --find --partscan /images/{0}
                        ExecStop=/usr/bin/losetup --detach-all
                        
                        [Install]
                        WantedBy=images.mount
                        """
                )
                .format(self._full_name)
                .encode("utf-8"),
                mode=0o644,
            )
            trace(
                "Wrote initrd-find-image-partitions (/images/{}".format(self._full_name)
            )

        return to_clean_up

    def _sd_boot_image_hook(self) -> str:
        hook = textwrap.dedent(
            """\
        #!/usr/bin/bash

        build() {
        """
        )
        if self._vg is not None:
            hook += """    # partprobe LV:
    add_systemd_unit "initrd-find-root-lv-partitions.service"
    """
            hook += (
                "    add_symlink \"/usr/lib/systemd/system/dev-{0}-{1}'"
                '.device.wants/initrd-find-root-lv-partitions.service" \\'.format(
                    self._vg, self._full_name
                )
            )
            hook += """
        "../initrd-find-root-lv-partitions.service"

"""
        if self._image_device is not None:
            escaped_device = _escape_device(self._image_device)
            hook += """
    # losetup image files:
    add_binary /usr/bin/losetup

    add_systemd_unit "images.mount"
    add_symlink "/usr/lib/systemd/system/{}.device.wants/images.mount" \
        "../images.mount"
    add_systemd_unit "initrd-find-image-partitions.service"
    add_symlink "/usr/lib/systemd/system/images.mount.wants/initrd-find-image-partitions.service" \
                "../initrd-find-image-partitions.service"
""".format(
                escaped_device
            )
        hook += textwrap.dedent(
            """\
        }
        
        help() {
            cat <<HELPEOF
        Enables booting from images stored in a filesystem or on a LV.
        HELPEOF
        }
        
        # vim: set ft=sh ts=4 sw=4 et:
        """
        )
        return hook

    def _install_mkinitcpio_hooks(
        self, location: Location, system_context: SystemContext
    ) -> typing.Sequence[str]:
        to_clean_up = [
            _create_install_hook(
                location,
                system_context,
                "sd-stateless",
                textwrap.dedent(
                    """\
                                 #!/usr/bin/bash
                                
                                 build() {
                                      # Setup rescue target:
                                      test -f "/etc/shadow.initramfs" && add_file "/etc/shadow.initramfs" "/etc/shadow"
                                      ### FIXME: Rescue target is broken in arch since libnss_files.so is missing its symlinks:-/
                                      BASE=$(cd /usr/lib ; readlink -f libnss_files.so)
                                      for i in $(ls /usr/lib/libnss_files.so*); do
                                          add_symlink "${i}" "${BASE}"
                                      done
                                 
                                     add_binary "/usr/bin/journalctl"
                                 
                                     # Setup etc:
                                     add_systemd_unit "initrd-sysroot-setup.service"
                                     add_symlink "/usr/lib/systemd/system/initrd.target.wants/initrd-sysroot-setup.service" \
                                                 "../initrd-sysroot-setup.service"
                                     
                                     # squashfs:
                                     add_module squashfs
                                     
                                     # /var setup
                                     if test -e "/usr/lib/systemd/system/sysroot-var.mount" ; then
                                         add_systemd_unit "sysroot-var.mount"
                                         add_symlink "/usr/lib/systemd/system/initrd-fs.target.wants/sysroot-var.mount" \
                                         "../sysroot-var.mount"
                                     fi
                                 }
                                 
                                 help() {
                                     cat <<HELPEOF
                                 This hook allows for setting up the rootfs from /usr/lib/boot/root-fs.tar.
                                 HELPEOF
                                 }
                                
                                 # vim: set ft=sh ts=4 sw=4 et:
                                 """
                ),
            ),
            _create_install_hook(
                location, system_context, "sd-boot-image", self._sd_boot_image_hook()
            ),
            _create_install_hook(
                location,
                system_context,
                "sd-verity",
                textwrap.dedent(
                    """\
                                 #!/usr/bin/bash
                                                                     
                                 build() {
                                     add_binary "/usr/lib/systemd/systemd-veritysetup"
                                     add_binary "/usr/lib/systemd/system-generators/systemd-veritysetup-generator"
                                     add_module dm-verity
                                 }
                                 
                                 help() {
                                     cat <<HELPEOF
                                 This hook allows for dm-verity setup
                                 HELPEOF
                                 }
                                 
                                 # vim: set ft=sh ts=4 sw=4 et:
                                 """
                ),
            ),
            _create_install_hook(
                location,
                system_context,
                "sd-volatile",
                textwrap.dedent(
                    """\
                                 #!/usr/bin/bash
                                
                                 build() {
                                     # volatile root:
                                     add_systemd_unit "systemd-volatile-root.service"
                                     add_symlink "/usr/lib/systemd/system/initrd.target.wants/systemd-volatile-root.service" \
                                     "../systemd-volatile-root.service"
                                     add_binary "/usr/lib/systemd/systemd-volatile-root"
                                 }
                                
                                 help() {
                                     cat <<HELPEOF
                                 This hook installs the necessary infrastructure for systemd.volatile to work.
                                 HELPEOF
                                 }
                                
                                 # vim: set ft=sh ts=4 sw=4 et:
                                 """
                ),
            ),
        ]

        return to_clean_up

    def _fix_mkinitcpio_conf(
        self, location: Location, system_context: SystemContext, name: str
    ):
        extra = system_context.substitution_expanded(
            "MKINITCPIO_EXTRA_{}".format(name), ""
        )
        if extra:
            self._execute(
                location.next_line(),
                system_context,
                "sed",
                "/^{}=/ c{}=({})".format(name, name, extra,),
                "/etc/mkinitcpio.conf",
            )

    def _install_mkinitcpio(
        self, location: Location, system_context: SystemContext
    ) -> typing.Sequence[str]:
        to_clean_up = ["/etc/mkinitcpio.d", "/etc/mkinitcpio.conf", "/boot/vmlinu*"]

        location.set_description("Install mkinitcpio")
        self._execute(location, system_context, "pacman", "mkinitcpio")

        location.set_description("Fix up mkinitcpio.conf")
        self._execute(
            location.next_line(),
            system_context,
            "sed",
            "/^HOOKS=/ "
            "cHOOKS=(base systemd keyboard sd-vconsole "
            "sd-encrypt block sd-lvm2 filesystems btrfs "
            "sd-stateless sd-verity sd-volatile sd-boot-image "
            "sd-shutdown)",
            "/etc/mkinitcpio.conf",
        )

        self._fix_mkinitcpio_conf(location.next_line(), system_context, "HOOKS")
        self._fix_mkinitcpio_conf(location.next_line(), system_context, "FILES")
        self._fix_mkinitcpio_conf(location.next_line(), system_context, "BINARIES")
        self._fix_mkinitcpio_conf(location.next_line(), system_context, "MODULES")

        self._execute(
            location.next_line(),
            system_context,
            "append",
            "/etc/mkinitcpio.conf",
            'COMPRESSION="cat"',
        )

        location.set_description("Create mkinitcpio presets")
        create_file(
            system_context,
            "/etc/mkinitcpio.d/cleanroom.preset",
            textwrap.dedent(
                """\
                    # mkinitcpio preset file for cleanroom

                    ALL_config="/etc/mkinitcpio.conf"
                    ALL_kver="/boot/vmlinuz"

                    PRESETS=('default')

                    #default_config="/etc/mkinitcpio.conf"
                    default_image="/boot/initramfs.img"
                    #default_options=""
                    """
            ).encode("utf-8"),
        )

        self._execute(
            location.next_line(),
            system_context,
            "sed",
            "s%/initramfs-linux.*.img%/initrd%",
            "/etc/mkinitcpio.d/cleanroom.preset",
        )

        return to_clean_up

    def _remove_mkinitcpio(
        self, location: Location, system_context: SystemContext
    ) -> None:
        # FIXME: Remove mkinitcpio once linux and ostree no longer depend on it!
        self._execute(
            location,
            system_context,
            "pacman",
            "mkinitcpio",
            "--assume-installed",
            "initramfs",
            "--assume-installed",
            "mkinitcpio",
            remove=True,
        )
        remove(system_context, "/boot/vmlinuz")

    def register_substitutions(self) -> typing.List[typing.Tuple[str, str, str]]:
        return [
            ("IMAGE_FS", "ext2", "The filesystem type to load clrm-images from",),
            ("IMAGE_DEVICE", "", "The device to load clrm-images from",),
            (
                "IMAGE_OPTIONS",
                "rw",
                "The filesystem options to mount the IMAGE_DEVICE with",
            ),
            (
                "DEFAULT_VG",
                "",
                "The volume group to look for clrm rootfs/verity partitions on",
            ),
            ("MKINITCPIO_EXTRA_MODULES", "", "Extra modules to add to the initrd",),
            ("MKINITCPIO_EXTRA_HOOKS", "", "Extra hooks to add to the initrd",),
            ("MKINITCPIO_EXTRA_BINARIES", "", "Extra binaries to add to the initrd",),
            ("MKINITCPIO_EXTRA_FILES", "", "Extra files to add to the initrd",),
        ]

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        if not os.path.exists(os.path.join(system_context.boot_directory, "vmlinuz")):
            info("Skipping initrd generation: No vmlinuz in boot directory.")
            return

        self._vg = system_context.substitution_expanded("DEFAULT_VG", "")
        if not self._vg:
            self._vg = None

        self._image_fs = system_context.substitution_expanded("IMAGE_FS", "")
        self._image_device = _device_ify(
            system_context.substitution_expanded("IMAGE_DEVICE", "")
        )
        self._image_options = system_context.substitution_expanded("IMAGE_OPTIONS", "")

        image_name = system_context.substitution_expanded("CLRM_IMAGE_FILENAME", "")
        self._full_name = image_name

        initrd = args[0]

        to_clean_up: typing.List[str] = []
        to_clean_up += "/boot/vmlinuz"
        to_clean_up += self._create_systemd_units(location, system_context)
        to_clean_up += self._install_mkinitcpio(location, system_context)
        to_clean_up += self._install_mkinitcpio_hooks(location, system_context)

        copy(
            system_context,
            os.path.join(system_context.boot_directory, "vmlinuz"),
            "/boot/vmlinuz",
            from_outside=True,
        )

        run(
            "/usr/bin/mkinitcpio",
            "-p",
            "cleanroom",
            chroot=system_context.fs_directory,
            chroot_helper=self._binary(Binaries.CHROOT_HELPER),
        )

        initrd_directory = os.path.dirname(initrd)
        os.makedirs(initrd_directory, exist_ok=True)
        move(system_context, "/boot/initramfs.img", initrd, to_outside=True)

        _cleanup_extra_files(location, system_context, *to_clean_up)
        self._remove_mkinitcpio(location, system_context)

        assert os.path.isfile(initrd)
