# -*- coding: utf-8 -*-
"""create_initrd command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd

import os.path


class CreateInitrdCommand(cmd.Command):
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
        location.next_line_offset('Installing extra mkinitcpio file {}'
                                  .format(file))
        source_path = os.path.join(self.helper_directory(), file)
        dest_path = os.path.join('/usr/bin', file)
        system_context.execute(location, 'copy', source_path, dest_path,
                               from_outside=True)
        return dest_path

    def _install_extra_binaries(self, location, system_context):
        to_clean_up = []
        to_clean_up.append(self._copy_extra_file(location, system_context,
                                                'initrd-check-bios.sh'))
        to_clean_up.append(self._copy_extra_file(location, system_context,
                                                'initrd-mnencode'))
        return to_clean_up

    def _install_mkinitcpio(self, location, system_context):
        to_clean_up = ['/etc/mkinitcpio.d/*', '/etc/mkinitcpio.conf',
                       '/boot/vmlinu*']

        location.next_line_offset('Install mkinitcpio')
        system_context.execute(location, 'pacman', 'mkinitcpio')

        location.next_line_offset('Fix up mkinitcpio.conf')
        system_context.execute(location, 'sed',
                               '/^HOOKS=/ '
                               'cHOOKS="base systemd keyboard sd-vconsole '
                               'sd-encrypt sd-lvm2 block filesystems '
                               'sd-check-bios sd-stateless sd-verity '
                               'sd-volatile sd-shutdown"',
                               '/etc/mkinitcpio.conf')

        location.next_line_offset('Fix up mkinitcpio presets')
        system_context.execute(location, 'sed',
                               "/^PRESETS=/ cPRESETS=('default')",
                               '/etc/mkinitcpio.d/linux.preset')
        system_context.execute(location, 'sed',
                               "/'fallback'/ d",
                               '/etc/mkinitcpio.d/linux.preset')
        system_context.execute(location, 'sed',
                               's%/vmlinuz-linux.*"%/vmlinuz"%',
                               '/etc/mkinitcpio.d/linux.preset')
        system_context.execute(location, 'sed',
                               's%/initramfs-linux.*.img%/initrd%',
                               '/etc/mkinitcpio.d/linux.preset')
        return to_clean_up

    def _create_install_hook(self, location, system_context, name, contents):
        location.next_line_offset('install mkinitcpio install hook {}'
                                  .format(name))
        path = os.path.join('/usr/lib/initcpio/install', name)
        system_context.execute(location, 'create', path, contents)
        return path

    def _install_mkinitcpio_hooks(self, location, system_context):
        to_clean_up = []
        to_clean_up.append(self._create_install_hook(location, system_context,
                                                     'sd-check-bios',
                                                     '''#!/bin/bash

build() {
    # Setup rescue target:
    add_binary "/usr/bin/initrd-check-bios.sh" "/usr/bin/check-bios.sh"
    add_binary "/usr/bin/initrd-mnencode" "/usr/bin/mnencode"
    add_binary "/usr/bin/md5sum"

    add_systemd_unit "initrd-check-bios.service"
    add_symlink "/usr/lib/systemd/system/initrd-root-device.target.wants/initrd-check-bios.service" \
                "../initrd-sysroot-setup.service"
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
                                                     '''#!/bin/bash

build() {
    # Setup rescue target:
    add_binary "/usr/bin/sulogin"
    test -f "/etc/shadow.initramfs" && add_file "/etc/shadow.initramfs" "/etc/shadow"

    add_binary "/usr/bin/journalctl"
    add_systemd_unit "rescue.service"
    add_systemd_unit "rescue.target"

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
This hook allows for setting up the rootfs from /usr/lib/modules/boot/rootfs.tar
HELPEOF
}

# vim: set ft=sh ts=4 sw=4 et:
'''))
        to_clean_up.append(self._create_install_hook(location, system_context,
                                                     'sd-verity',
                                                     '''#!/bin/bash

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
                                                     '''#!/bin/bash

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
        location.next_line_offset('Run mkinitcpio')
        system_context.run('/usr/bin/mkinitcpio', '-p', 'linux')

    def _cleanup_extra_files(self, location, system_context, *files):
        location.next_line_offset('Remove extra mkinitcpio files')
        system_context.execute(location, 'remove', *files, force=True)

    def _remove_mkinitcpio(self, location, system_context):
        # FIXME: Remove mkinitcpio once linux and ostree no longer depend on it!
        # system_context.execute(location, 'pacman', 'mkinitcpio', remove=True)
        pass

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        initrd = args[0]

        to_clean_up = []
        to_clean_up += self._install_extra_binaries(location, system_context)
        to_clean_up += self._install_mkinitcpio(location, system_context)
        to_clean_up += self._install_mkinitcpio_hooks(location, system_context)

        self._run_mkinitcpio(location, system_context)

        initrd_directory = os.path.dirname(initrd)
        if not os.path.isdir(initrd_directory):
            os.makedirs(initrd_directory)
        system_context.execute(location, 'move', '/boot/initrd', initrd,
                               to_outside=True)

        self._cleanup_extra_files(location, system_context, *to_clean_up)
        self._remove_mkinitcpio(location, system_context)
