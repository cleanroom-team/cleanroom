# -*- coding: utf-8 -*-
"""create_initrd command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext
import cleanroom.generator.helper.generic.file as filehelper
from cleanroom.printer import info

import os.path
import typing


def _deviceify(device: str) -> str:
    if device.startswith('PARTLABEL='):
        device = '/dev/disk/by-partlabel/' + device[10:]
    elif device.startswith('LABEL='):
        device = '/dev/disk/by-label/' + device[6:]
    elif device.startswith('PARTUUID='):
        device = '/dev/disk/by-partuuid/' + device[9:]
    elif device.startswith('UUID='):
        device = '/dev/disk/by-uuid/' + device[5:]
    elif device.startswith('ID='):
        device = '/dev/disk/by-id/' + device[3:]
    elif device.startswith('PATH='):
        device = '/dev/disk/by-path/' + device[5:]
    assert device.startswith('/dev/')
    return device


def _escape_device(device: str) -> str:
    device = _deviceify(device)

    device = device.replace('-', '\\x2d')
    device = device.replace('=', '\\x3d')
    device = device.replace(';', '\\x3b')
    device = device.replace('/', '-')

    return device[1:]


def _install_mkinitcpio(location: Location, system_context: SystemContext) \
        -> typing.Sequence[str]:
    to_clean_up = ['/etc/mkinitcpio.d', '/etc/mkinitcpio.conf',
                   '/boot/vmlinu*']

    location.set_description('Install mkinitcpio')
    system_context.execute(location.next_line(), 'pacman', 'mkinitcpio')

    location.set_description('Fix up mkinitcpio.conf')
    system_context.execute(location.next_line(), 'sed',
                           '/^HOOKS=/ '
                           'cHOOKS="base systemd keyboard sd-vconsole '
                           'sd-encrypt block sd-lvm2 filesystems btrfs '
                           'sd-check-bios sd-stateless sd-verity '
                           'sd-volatile sd-boot-image '
                           'sd-shutdown"',
                           '/etc/mkinitcpio.conf')

    location.set_description('Fix up mkinitcpio presets')
    system_context.execute(location.next_line(), 'sed',
                           "/^PRESETS=/ cPRESETS=('default')",
                           '/etc/mkinitcpio.d/cleanroom.preset')
    system_context.execute(location.next_line(), 'sed',
                           "/'fallback'/ d",
                           '/etc/mkinitcpio.d/cleanroom.preset')
    system_context.execute(location.next_line(), 'sed',
                           's%/vmlinuz-linux.*"%/vmlinuz"%',
                           '/etc/mkinitcpio.d/cleanroom.preset')
    system_context.execute(location.next_line(), 'sed',
                           's%/initramfs-linux.*.img%/initrd%',
                           '/etc/mkinitcpio.d/cleanroom.preset')
    return to_clean_up


def _create_install_hook(location: Location, system_context: SystemContext,
                         name: str, contents: str) -> str:
    location.set_description('install mkinitcpio install hook {}'
                             .format(name))
    path = os.path.join('/usr/lib/initcpio/install', name)
    filehelper.create_file(system_context, path, contents.encode('utf-8'))
    return path


def _run_mkinitcpio(location: Location, system_context: SystemContext) -> None:
    location.set_description('Run mkinitcpio')
    system_context.run('/usr/bin/mkinitcpio', '-p', 'cleanroom')


def _cleanup_extra_files(location: Location, system_context: SystemContext,
                         *files: str) -> None:
    location.set_description('Remove extra mkinitcpio files')
    filehelper.remove(system_context, *files, force=True, recursive=True)


class CreateInitrdCommand(Command):
    """The create_initrd command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('create_initrd', syntax='<INITRD_FILE>',
                         help_string='Create an initrd.', file=__file__)

        self._vg = None  # type: typing.Optional[str]
        self._image_fs = None  # type: typing.Optional[str]
        self._image_device = None  # type: typing.Optional[str]
        self._image_options = None  # type: typing.Optional[str]

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_arguments_exact(location, 1,
                                       '"{}" takes an initrd to create.',
                                       *args, **kwargs)

        return None

    def _copy_extra_file(self, location: Location, system_context: SystemContext,
                         extra_file: str) -> str:
        location.set_description('Installing extra mkinitcpio file {}'
                                 .format(extra_file))
        helper_directory = self.helper_directory()
        assert helper_directory
        source_path = os.path.join(helper_directory, extra_file)
        dest_path = os.path.join('/usr/bin', extra_file)
        filehelper.copy(system_context, source_path, dest_path, from_outside=True)
        filehelper.chmod(system_context, 0o755, dest_path)
        return dest_path

    def _install_extra_binaries(self, location: Location, system_context: SystemContext) \
            -> typing.Sequence[str]:
        to_clean_up: typing.List[str] = [self._copy_extra_file(location, system_context,
                                                               'initrd-check-bios.sh'),
                                         self._copy_extra_file(location, system_context,
                                                               'initrd-mnencode')]
        return to_clean_up

    def _create_systemd_units(self, location: Location, system_context: SystemContext) \
            -> typing.Sequence[str]:
        location.set_description('Install extra systemd units')
        to_clean_up = ['/usr/lib/systemd/system/initrd-check-bios.service',
                       '/usr/lib/systemd/system/initrd-sysroot-setup.service',
                       '/usr/lib/systemd/system/initrd-find-root-lv-partitions.service',
                       '/usr/lib/systemd/system/images.mount',
                       '/usr/lib/systemd/system/initrd-find-image-partitions.service']
        filehelper.create_file(system_context, '/usr/lib/systemd/system/initrd-check-bios.service',
                               '''[Unit]
Description=Print TPM configuration
DefaultDependencies=no
Requires=sysroot.mount
After=sysroot.mount systemd-volatile-root.service
Before=initrd-root-fs.target shutdown.target
Conflicts=shutdown.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/initrd-check-bios.sh
StandardOutput=journal+console

[Install]
WantedBy=initrd-root-device.target
'''.encode('utf-8'), mode=0o644)

        filehelper.create_file(system_context, '/usr/lib/systemd/system/initrd-sysroot-setup.service',
                               '''[Unit]
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
'''.encode('utf-8'), mode=0o644)

        if self._vg is not None:
            device_name = 'dev-{}-{}'.format(self._vg, self._full_name)
            filehelper.create_file(system_context, '/usr/lib/systemd/system/initrd-find-root-lv-partitions.service',
                                   '''[Unit]
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
'''.format(device_name, self._vg, self._full_name).encode('utf-8'), mode=0o644)

        if self._image_device is not None:
            filehelper.create_file(system_context, '/usr/lib/systemd/system/images.mount',
                                   '''[Unit]
Description=Mount /images in initrd
DefaultDependencies=no
After=systemd-cryptsetup@main.service

[Mount]
What={}
Where=/images
Type={}
Options={}
'''.format(self._image_device, self._image_fs, self._image_options)
                                   .encode('utf-8'), mode=0o644)

            filehelper.create_file(system_context, '/usr/lib/systemd/system/initrd-find-image-partitions.service',
                                   '''[Unit]
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
'''.format(self._full_name).encode('utf-8'), mode=0o644)

        return to_clean_up

    def _sd_boot_image_hook(self) -> str:
        hook = '''#!/usr/bin/bash

build() {
'''
        if self._vg is not None:
            hook += '''
    # partprobe LV:
    add_systemd_unit "initrd-find-root-lv-partitions.service"
'''
            hook += "    add_symlink \"/usr/lib/systemd/system/dev-{0}-{1}'" \
                    ".device.wants/initrd-find-root-lv-partitions.service\" \\" \
                .format(self._vg, self._full_name)
            hook += '''
        "../initrd-find-root-lv-partitions.service"

'''
        if self._image_device is not None:
            escaped_device = _escape_device(self._image_device)
            hook += '''
    # losetup image files:
    add_binary /usr/bin/losetup

    add_systemd_unit "images.mount"
    add_symlink "/usr/lib/systemd/system/{}.device.wants/images.mount" \
        "../images.mount"
    add_systemd_unit "initrd-find-image-partitions.service"
    add_symlink "/usr/lib/systemd/system/images.mount.wants/initrd-find-image-partitions.service" \
                "../initrd-find-image-partitions.service"
'''.format(escaped_device)
        hook += '''
}

help() {
    cat <<HELPEOF
Enables booting from images stored in a filesystem or on a LV.
HELPEOF
}

# vim: set ft=sh ts=4 sw=4 et:
'''
        return hook

    def _install_mkinitcpio_hooks(self, location: Location, system_context: SystemContext) \
            -> typing.Sequence[str]:
        to_clean_up = [
            _create_install_hook(location, system_context,
                                 'sd-check-bios', '''#!/usr/bin/bash

build() {
# Setup rescue target:
add_binary "/usr/bin/initrd-check-bios.sh"
add_binary "/usr/bin/initrd-mnencode"
add_binary "/usr/bin/md5sum"

add_systemd_unit "initrd-check-bios.service"
add_symlink "/usr/lib/systemd/system/initrd-root-device.target.wants/initrd-check-bios.service" \
            "../initrd-check-bios.service"
add_module tpm_tis tpm_atmel tpm_nsc
}

help() {
cat <<HELPEOF
This hook will enable printing a passphrase with TPM registers
HELPEOF
}

# vim: set ft=sh ts=4 sw=4 et:
'''),
            _create_install_hook(location, system_context,
                                 'sd-stateless', '''#!/usr/bin/bash

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
'''),
            _create_install_hook(location, system_context,
                                 'sd-boot-image',
                                 self._sd_boot_image_hook()),
            _create_install_hook(location, system_context,
                                 'sd-verity',
                                 '''#!/usr/bin/bash

build() {
    add_binary "/usr/lib/systemd/systemd-veritysetup"
    add_binary "/usr/lib/systemd/system-generators/systemd-veritysetup-generator"
    add_module dm-verity
}

help() {
    cat <<HELPEOF
This hook allows for dm-verity setup via systemd.verity=true
HELPEOF
}

# vim: set ft=sh ts=4 sw=4 et:
'''),
            _create_install_hook(location, system_context,
                                 'sd-volatile',
                                 '''#!/usr/bin/bash

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
''')]

        return to_clean_up

    def _remove_mkinitcpio(self, location: Location,
                           system_context: SystemContext) -> None:
        # FIXME: Remove mkinitcpio once linux and ostree no longer depend on it!
        # system_context.execute(location, 'pacman', 'mkinitcpio', remove=True)
        pass

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        if not os.path.exists(system_context.file_name('usr/bin/mkinitcpio')):
            info('Skipping initrd generation: No mkinitcpio binary.')
            return

        if not os.path.exists(os.path.join(system_context.boot_data_directory(),
                                           'vmlinuz')):
            info('Skipping initrd generation: No vmlinuz in boot directory.')
            return

        self._vg = system_context.substitution('DEFAULT_VG', None)
        if not self._vg:
            self._vg = None

        self._image_fs = system_context.substitution('IMAGE_FS', 'ext2')
        self._image_device = \
            _deviceify(system_context.substitution('IMAGE_DEVICE', ''))
        self._image_options = system_context.substitution('IMAGE_OPTIONS', 'rw')

        name_prefix = system_context.substitution('DISTRO_ID', 'clrm')
        name_version = system_context.substitution('DISTRO_VERSION_ID', system_context.timestamp)
        self._full_name = "{}_{}".format(name_prefix, name_version)

        initrd = args[0]

        to_clean_up = []  # type: typing.List[str]
        to_clean_up += self._install_extra_binaries(location, system_context)
        to_clean_up += self._create_systemd_units(location, system_context)
        to_clean_up += _install_mkinitcpio(location, system_context)
        to_clean_up += self._install_mkinitcpio_hooks(location, system_context)

        _run_mkinitcpio(location, system_context)

        initrd_directory = os.path.dirname(initrd)
        os.makedirs(initrd_directory, exist_ok=True)
        filehelper.move(system_context, '/boot/initrd', initrd, to_outside=True)

        _cleanup_extra_files(location, system_context, *to_clean_up)
        self._remove_mkinitcpio(location, system_context)
