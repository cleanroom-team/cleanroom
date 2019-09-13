Pacman:
 * Remove /usr/lib/libalpm with hooks, etc.?
 * Use --hookdir to override default hooks?

option infrastructure:
  * option_cpu_intel
  * option_gpu_intel

* Make verity partition name configurable (uuid is used anyway:-)
* Fix imager not to depend on clrm_* for root partitions [fixme]

* No /var/log/journal in VM. Normal?
* /var/log/pacman.log: Where does that come from? pacstrap
  should delete that in _teardown hook

* Remove jack [test]

* export_rootfs:
   * create_export_directory -- should work
   * tarball creation and storage

* alacritty support on ron is missing:-/

* Use erofs over squashfs (once available)
* Move to dracut for initrd generation

* Remove C! lines from usr/lib/tmpfiles.d/etc.conf
