# Cleanroom

Cleanroom makes it easy and fast to do fresh installations of whole
fleets of machines (bare metal, VMs or containers).

A set of system descriptions is used to describe the machines to be
installed. Cleanroom will use this description and files downloaded
from Linux Distributions to do the actual installations.

By enabling easy and fast installations, Cleanroom enables the use
of immutable and stateless systems as it becomes feasible to keep
such machines up-to-date by simply regenerating a fresh image and
booting into it.

Up-to-date code can be found at:

   https://github.com/cleanroom-team/cleanroom


## Installation

Just use the code straight from the repository:-)

### Optional Build Container

If you do not want your systems to be built in your normal OS setup,
you can create an optional build container for Cleanroom.

```
pacstrap clrm-archlinux \
    arch-install-scripts \
    binutils borg btrfs-progs \
    cpio \
    devtools dosfstools \
    lsof \
    nbd \
    pacman python-pyparsing \
    qemu \
    sbsigntools \
    squashfs-tools \
    tar
```

should get you started.

Use

```
build_container \
    --build-container=clrm-archlinux \
    --systems-directory=/SYSTEMS/DIRECTORY \
    --work-directory=/WORK/DIR \
    --repository-base-directory=/REPOSITORY/BASE \
    clrm --verbose --verbose --verbose --verbose \
    --clear-scratch-directory \
    SYSTEM_NAME
```

to build inside this container.

## Tests

Use ```pytest tests``` in the top level directory to run all tests.

## Contributors

* Tobias Hunger &lt;tobias.hunger@gmail.com&gt;

## Code of Conduct

Everybody is expected to follow the Python Community Code of Conduct
https://www.python.org/psf/codeofconduct/

## License

All files in cleanroom are under GPL v3 (or later).

See LICENSE.md for the full license text.
