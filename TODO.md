create_initrd.py:
  * Test

option infrastructure:
  * option_cpu_intel
  * option_gpu_intel

Examine current system: Does it look functional?

* Generate /usr/lib/os-release from DISTRO_* substitutions
* Do not install systemd loop-hook when no LVM is used
* Make verity partition name configurable (uuid is used anyway:-)
* Fix imager not to depend on clrm_* for root partitions
