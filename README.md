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

   https://gitlab.com/cleanroom/cleanroom


## Installation

Use python setuptools as usual.

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
