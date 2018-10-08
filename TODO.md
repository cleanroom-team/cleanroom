Pacman:
 * Remove /usr/lib/libalpm with hooks, etc.?
 * Use --hookdir to override default hooks?

create_initrd.py:
  * Test

option infrastructure:
  * option_cpu_intel
  * option_gpu_intel

Examine current system: Does it look functional?

* Generate /usr/lib/os-release from DISTRO_* substitutions [test]
* Do not install systemd loop-hook when no LVM is used
* Make verity partition name configurable (uuid is used anyway:-)
* Fix imager not to depend on clrm_* for root partitions [fixme]

* No /var/log/journal in VM. Normal?
* /var/log/pacman.log: Where does that come from? pacstrap
  should delete that in _teardown hook

* FIX multiline args starting with 4 spaces

* Add git [test]

