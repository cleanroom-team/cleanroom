# -*- coding: utf-8 -*-
"""create_initrd command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command

import os.path


class CreateInitrdCommand(Command):
    """The create_initrd command."""

    def __init__(self):
        """Constructor."""
        super().__init__('create_initrd', syntax='<INITRD_FILE>',
                         help='Create an initrd.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_exact(location, 1,
                                  '"{}" takes an initrd to create.',
                                  *args, **kwargs)

    def _copy_extra_file(self, location, system_context, file):
        location.set_description('Installing extra mkinitcpio file {}'
                                  .format(file))
        source_path = os.path.join(self.helper_directory(), file)
        dest_path = os.path.join('/usr/bin', file)
        system_context.execute(location.next_line(), 'copy', source_path, dest_path,
                               from_outside=True)
        return dest_path

    def _install_extra_binaries(self, location, system_context):
        to_clean_up = []
        to_clean_up.append(self._copy_extra_file(location, system_context,
                                                'initrd-check-bios.sh'))
        to_clean_up.append(self._copy_extra_file(location, system_context,
                                                'initrd-mnencode'))
        return to_clean_up

    def _create_systemd_units(self, location, system_context):
        location.set_description('Install extra systemd units')
        to_clean_up = ['/usr/lib/systemd/system/initrd-check-bios.service',
                       '/usr/lib/systemd/system/initrd-sysroot-setup.service',
                       '/usr/lib/systemd/system/initrd-find-root-lv-partitions.service',
                       '/usr/lib/systemd/system/images.mount',
                       '/usr/lib/systemd/system/initrd-find-image-partitions.service']
        system_context.execute(location.next_line(), 'create', '/usr/lib/systemd/system/initrd-check-bios.service',
                               '''[Unit]
Description=Print TPM configuration
Before=initrd-root-device.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/initrd-check-bios.sh
StandardOutput=journal+console

[Install]
WantedBy=initrd-root-device.target
''', mode=0o644)

        system_context.execute(location.next_line(), 'create', '/usr/lib/systemd/system/initrd-sysroot-setup.service',
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
''', mode=0o644)

        device_name = 'dev-{}-{}'.format(self._vg, self._full_name)
        system_context.execute(location.next_line(), 'create', '/usr/lib/systemd/system/initrd-find-root-lv-partitions.service',
                               '''[Unit]
Description=Find partitions in root LV
DefaultDependencies=no
After={0}.device
BindsTo={0}.device
Requisite={0}.device

[Service]
WorkingDirectory=/
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/losetup --partscan --find /dev/{1}/{2}
ExecStop=/usr/bin/losetup --detach-all

[Install]
WantedBy={0}.device
'''.format(device_name, self._vg, self._full_name), mode=0o644)

        system_context.execute(location.next_line(), 'create', '/usr/lib/systemd/system/images.mount',
                               '''[Unit]
Description=Mount /images in initrd
DefaultDependencies=no
Conflicts=umount.target
Before=local-fs.target unmount.target

[Mount]
What=/dev/disk/by-partlabel/IMAGES
Where=/images
Type=ext2
Options=ro
''', mode=0o644)

        system_context.execute(location.next_line(), 'create', '/usr/lib/systemd/system/initrd-find-image-partitions.service',
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
ExecStart=/usr/bin/losetup --partscan --find /images/{0}
ExecStop=/usr/bin/losetup --detach-all

[Install]
WantedBy=images.mount
'''.format(self._full_name), mode=0o644)

        return to_clean_up

    def _install_mkinitcpio(self, location, system_context):
        to_clean_up = ['/etc/mkinitcpio.d', '/etc/mkinitcpio.conf',
                       '/boot/vmlinu*']

        location.set_description('Install mkinitcpio')
        system_context.execute(location.next_line(), 'pacman', 'mkinitcpio')

        location.set_description('Fix up mkinitcpio.conf')
        system_context.execute(location.next_line(), 'sed',
                               '/^HOOKS=/ '
                               'cHOOKS="base systemd keyboard sd-vconsole '
                               'sd-encrypt sd-lvm2 block filesystems '
                               'sd-check-bios sd-stateless sd-verity '
                               'sd-volatile sd-boot-image '
                               'sd-shutdown"',
                               '/etc/mkinitcpio.conf')

        location.set_description('Fix up mkinitcpio presets')
        system_context.execute(location.next_line(), 'sed',
                               "/^PRESETS=/ cPRESETS=('default')",
                               '/etc/mkinitcpio.d/linux.preset')
        system_context.execute(location.next_line(), 'sed',
                               "/'fallback'/ d",
                               '/etc/mkinitcpio.d/linux.preset')
        system_context.execute(location.next_line(), 'sed',
                               's%/vmlinuz-linux.*"%/vmlinuz"%',
                               '/etc/mkinitcpio.d/linux.preset')
        system_context.execute(location.next_line(), 'sed',
                               's%/initramfs-linux.*.img%/initrd%',
                               '/etc/mkinitcpio.d/linux.preset')
        return to_clean_up

    def _create_install_hook(self, location, system_context, name, contents):
        location.set_description('install mkinitcpio install hook {}'
                                  .format(name))
        path = os.path.join('/usr/lib/initcpio/install', name)
        system_context.execute(location.next_line(), 'create', path, contents)
        return path

    def _sd_boot_image_hook(self):
        hook = '''#!/usr/bin/bash

build() {
'''
        if self._vg:
            hook += '''
    # losetup LV:
    add_systemd_unit "initrd-find-root-lv-partitions.service"
'''
            hook += "    add_symlink \"/usr/lib/systemd/system/dev-{0}-{1}.device.wants/initrd-find-root-lv-partitions.service\" \\"\
                 .format(self._vg, self._full_name)
            hook += '''
        "../initrd-find-root-lv-partitions.service"

'''
        hook += '''
    # losetup image files:
    add_systemd_unit "images.mount"
    add_symlink "/usr/lib/systemd/system/dev-disk-by\\\\x2dpartlabel-IMAGES.device.wants/images.mount" \
        "../images.mount"
    add_systemd_unit "initrd-find-image-partitions.service"
    add_symlink "/usr/lib/systemd/system/images.mount.wants/initrd-find-image-partitions.service" \
                "../initrd-find-image-partitions.service"
}

help() {
    cat <<HELPEOF
Enables booting from images stored in a filesystem or on a LV.
HELPEOF
}

# vim: set ft=sh ts=4 sw=4 et:
'''
        return hook

    def _install_mkinitcpio_hooks(self, location, system_context):
        to_clean_up = []
        to_clean_up.append(self._create_install_hook(location, system_context,
                                                     'sd-check-bios',
                                                     '''#!/usr/bin/bash

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
'''))

        to_clean_up.append(self._create_install_hook(location, system_context,
                                                     'sd-stateless',
                                                     '''#!/usr/bin/bash

build() {
    # Setup rescue target:
    test -f "/etc/shadow.initramfs" && add_file "/etc/shadow.initramfs" "/etc/shadow"
    ### FIXME: Rescue target is broken in arch since libnss_files.so is missing its symlinks:-/
    BASE=$$(cd /usr/lib ; readlink -f libnss_files.so)
    for i in $$(ls /usr/lib/libnss_files.so*); do
        add_symlink "$${i}" "$${BASE}"
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
'''))

        to_clean_up.append(self._create_install_hook(location, system_context,
                                                     'sd-boot-image',
                                                     self._sd_boot_image_hook()))

        to_clean_up.append(self._create_install_hook(location, system_context,
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
'''))

        to_clean_up.append(self._create_install_hook(location, system_context,
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
'''))

        return to_clean_up

    def _run_mkinitcpio(self, location, system_context):
        location.set_description('Run mkinitcpio')
        system_context.run('/usr/bin/mkinitcpio', '-p', 'linux')

    def _cleanup_extra_files(self, location, system_context, *files):
        location.set_description('Remove extra mkinitcpio files')
        system_context.execute(location.next_line(), 'remove', *files, force=True, recursive=True)

    def _remove_mkinitcpio(self, location, system_context):
        # FIXME: Remove mkinitcpio once linux and ostree no longer depend on it!
        # system_context.execute(location, 'pacman', 'mkinitcpio', remove=True)
        pass

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        self._vg = system_context.substitution('DEFAULT_VG', 'vg_int')
        name_prefix = system_context.substitution('DISTRO_ID', 'clrm')
        name_version = system_context.substitution('DISTRO_VERSION_ID', system_context.timestamp)
        self._full_name = "{}_{}".format(name_prefix, name_version)

        initrd = args[0]

        to_clean_up = []
        to_clean_up += self._install_extra_binaries(location, system_context)
        to_clean_up += self._create_systemd_units(location, system_context)
        to_clean_up += self._install_mkinitcpio(location, system_context)
        to_clean_up += self._install_mkinitcpio_hooks(location, system_context)

        self._run_mkinitcpio(location, system_context)

        initrd_directory = os.path.dirname(initrd)
        os.makedirs(initrd_directory, exist_ok=True)
        system_context.execute(location.next_line(), 'move', '/boot/initrd', initrd,
                               to_outside=True)

        # self._cleanup_extra_files(location, system_context, *to_clean_up)
        self._remove_mkinitcpio(location, system_context)
