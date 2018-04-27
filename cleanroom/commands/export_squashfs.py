# -*- coding: utf-8 -*-
"""export_squashfs command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.exportcommand as cmd

import cleanroom.helper.generic.btrfs as btrfs


class ExportSquashfsCommand(cmd.ExportCommand):
    """The export_squashfs Command."""

    def __init__(self):
        """Constructor."""
        super().__init__('export_squashfs',
                         help='Export the root filesystem as squashfs.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate arguments."""
        return self._validate_no_arguments(location, *args, **kwargs)

    def _store_rootfs():
# HEADLINE Storing /etc and /root
# RAW test -e "${tarball}" && exit 17
# RAW if test -d "$tarlocation"; then
# RAW     ( cd "\${ROOT}" && tar -cf "$tarball" --sort=name etc root ) || exit 1
# RAW     echo "    > Root FS stored for later use."
# RAW else
# RAW     echo "    > Root FS NOT stored for later use."
# RAW     exit 15
# RAW fi

# RAW mkdir -p "\${ROOT}/usr/lib/modules/boot"
# RAW cp "\${BOOT_DATA_DIR}/rootfs.tar" "\${ROOT}/usr/lib/modules/boot"
        pass

    def _create_initramfs():
        pass

    def _create_root_tarball():
        pass

    def _create_squashfs():
# RAW _VG=\$(echo -n "vg_\${SYSTEM_NAME#system-}" | tr -c "[a-z0-9]" "_")
#
# HEADLINE Setting up squashfs
# RAW mkdir -p "\${EXPORT_DIR}/parts"
# RAW ( cd "\${ROOT}" && mksquashfs usr "\${EXPORT_DIR}/$squashfile" -comp lz4 -noappend -no-exports -keep-as-directory )
# RAW SQUASHFS_SIZE=\$(stat -c%s "\${EXPORT_DIR}/$squashfile")
# RAW SQUASHFS_TARGET_SIZE=\$(( ( (\${SQUASHFS_SIZE} + (4 * 1024*1024)) / (4 * 1024*1024) ) * 4 * 1024*1024 ))
# RAW SQUASHFS_TO_APPEND_SIZE=\$(( \${SQUASHFS_TARGET_SIZE} - \${SQUASHFS_SIZE} ))
# RAW dd "bs=\${SQUASHFS_TO_APPEND_SIZE}" count=1 if=/dev/zero >> "\${EXPORT_DIR}/$squashfile"
#
# RAW echo "Expanding $squashfile from \${SQUASHFS_SIZE} by \${SQUASHFS_TO_APPEND_SIZE} to \${SQUASHFS_TARGET_SIZE}..."
        pass

    def _create_dmverity():
# HEADLINE Setting up dm-verity
# RAW VERITY_ROOT_HASH=\$( cd "\${EXPORT_DIR}" && veritysetup format "$squashfile" "$verityfile" | grep "Root hash:" )
# RAW test -e "\${EXPORT_DIR}/$verityfile" || exit 62
# RAW VERITY_ROOT_HASH=\$( echo "\${VERITY_ROOT_HASH}" | sed -e 's/^Root hash:[ \\t]*//; s/[ \\t]*\$//' )
# RAW echo "Verity hash is \${VERITY_ROOT_HASH}..."
# RAW echo "\${VERITY_ROOT_HASH}" | grep -Eq '^[0-9a-fA-F]+\$' > /dev/null || exit 64
#
# RAW VERITY_SIZE=\$( stat -c%s "\${EXPORT_DIR}/$verityfile" )
# RAW VERITY_TARGET_SIZE=\$(( ( (\${VERITY_SIZE} + (4 * 1024*1024)) / (4 * 1024*1024) ) * 4 * 1024*1024 ))
# RAW VERITY_TO_APPEND_SIZE=\$(( \${VERITY_TARGET_SIZE} - \${VERITY_SIZE} ))
# RAW dd "bs=\${SQUASHFS_TO_APPEND_SIZE}" count=1 if=/dev/zero >> "\${EXPORT_DIR}/$verityfile"
#
# RAW echo "Expanding $verityfile from \${VERITY_SIZE} by \${VERITY_TO_APPEND_SIZE} to \${VERITY_TARGET_SIZE}..."
        pass

    def _setup_kernel_commandline():
#
# RAW _VERITY_DEV=\$(echo "root_\${TIMESTAMP}" | sed -e "s/-/--/g")
#
# RAW test -e "\${KERNEL_CMDLINE}" || touch "\${KERNEL_CMDLINE}"
# # Add FOO last so that ron can savely drop the last character of the commandline:-/
# RAW echo -n " rd.systemd.verity=yes roothash=\${VERITY_ROOT_HASH} systemd.verity_root_data=/dev/mapper/\${_VG}-\${_VERITY_DEV} systemd.verity_root_hash=/dev/mapper/\${_VG}-\${_VERITY_DEV}_verity FOO" >> "\${KERNEL_CMDLINE}"
#
        pass

    def _secure_boot():
        # INSECURE_BOOT
#* HEADLINE Creating linux.efi
#* RAW _KCMD="\${KERNEL_CMDLINE}"
#* RAW test -e "\${_KCMD}" || exit 4
#* RAW _KERNEL_CMD="\$(cat \"\${_KCMD}\")"
#* RAW readonly _TMP_DIR="\$(mktemp -d -t cmdline.XXXXXX)"
#* RAW _CMDFILE="\${_TMP_DIR}/commandline"
#* RAW echo -ne "\${_KERNEL_CMD}" | tr '\\n' ' ' | sed -e "s/^\\s*//" | sed -e "s/\\s*\$//" > "\${_CMDFILE}" && echo -ne "\x00\x00" >> "\${_CMDFILE}"
#* RAW  _INITRD="\${_TMP_DIR}/initrd"
#* RAW if test -e "\${BOOT_DATA_DIR}/ucode" ; then
#* RAW     cat "\${BOOT_DATA_DIR}/ucode" > "\${_INITRD}"
#* RAW else
#* RAW     touch "\${_INITRD}"
#* RAW fi
#* RAW cat "\${BOOT_DATA_DIR}/initrd" >> "\${_INITRD}"
#*
#* RAW objcopy --add-section .osrel="\${ROOT}/usr/lib/os-release" --change-section-vma .osrel=0x20000 --add-section .cmdline="\${_CMDFILE}" --change-section-vma .cmdline=0x30000 --add-section .linux="\${BOOT_DATA_DIR}/vmlinuz" --change-section-vma .linux=0x40000 --add-section .initrd="\${_INITRD}" --change-section-vma .initrd=0x3000000 "\${ROOT}/usr/lib/systemd/boot/efi/linuxx64.efi.stub" "\${BOOT_DATA_DIR}/linux.efi"
#*
#* RAW mv "\${_CMDFILE}" "\${KERNEL_CMDLINE}"
#*
#* RAW rm -rf "\${_TMP_DIR}"

        #
        # SIGN_EFI_BINARY "/boot/linux.efi" "/boot/linux.efi.signed"
        # RAW mv "\${BOOT_DATA_DIR}/linux.efi.signed" "\${BOOT_DATA_DIR}/linux-\${TIMESTAMP}.efi"
        # RAW rm -f "\${BOOT_DATA_DIR}/linux.efi"

        pass

    def create_export_directory(self, system_context):
        """Return the root directory."""
        export_volume = os.path.join(system_context.fs_directory(), 'export')
        btrfs.create_subvolume(system_context, export_volume)

        self._store_rootfs()
        self._create_initramfs()
        self._create_root_tarball()
        self._create_squashfs()
        self._create_dmverity()
        self._setup_kernel_commandline()
        self._secure_boot()

        return export_volume

    def delete_export_directory(self, system_context, export_directory):
        """Nothing to see, move on."""
        pass  # Filesystem will be cleaned up automatically.

# SECURE_BOOT
#
# HEADLINE Export kernel and data
# RAW ( cd "\${EXPORT_BASE}" && ln -s "\${ROOTNAME}" "\${ROOTLINK}" )
#
# RAW mv "\${KERNEL_CMDLINE}" "\${BOOT_DATA_DIR}/vmlinuz" "\${BOOT_DATA_DIR}/initrd" "\${EXPORT_DIR}/parts"
# RAW mv "\${BOOT_DATA_DIR}/linux-\${TIMESTAMP}.efi" "\${EXPORT_DIR}"
