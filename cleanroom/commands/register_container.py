"""register_container command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.helper.file import exists
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os.path
import textwrap
import typing


def _nspawn_ify(what: str, *systems: str) -> str:
    clean = [s for s in systems if s]
    if len(clean) > 0:
        return "\n{}={}".format(what, " ".join(*clean))
    return ""


class RegisterContainerCommand(Command):
    """The register_container command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "register_container",
            syntax="<SYSTEM> "
            "description=<DESC> "
            "timeout=3m after=<SYSTEM>(,<SYSTEM>)* "
            "requires=<SYSTEM>(,<SYSTEM>)*"
            "enable=False",
            help_string="Register a container with a system.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_args_exact(
            location, 1, '"{}" needs a system to ' "install as a container.", *args
        )
        self._validate_kwargs(
            location,
            ("description", "after", "requires", "timeout", "enable"),
            **kwargs
        )
        self._require_kwargs(location, ("description",), **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        system = args[0]
        description = kwargs.get("description", "")
        after_input = kwargs.get("after", "")
        requires_input = kwargs.get("requires", "")
        timeout = kwargs.get("timeout", "3m")
        enable = kwargs.get("enable", False)

        bin_directory = "/usr/bin"
        systemd_directory = "/usr/lib/systemd/system"

        location.set_description("Update update-all-containers.sh")
        updater_script = os.path.join(bin_directory, "update-all-containers.sh")

        if not exists(system_context, updater_script):
            self._execute(
                location.next_line(),
                system_context,
                "create",
                updater_script,
                "#!/usr/bin/bash\n",
            )
        self._execute(
            location.next_line(),
            system_context,
            "append",
            updater_script,
            '/usr/bin/update-container.sh "{}" || exit 1\n',
        )

        location.set_description("")
        override_dir = "{}/systemd-nspawn@{}.service.d".format(
            systemd_directory, system
        )
        self._execute(location.next_line(), system_context, "mkdir", override_dir)

        after = _nspawn_ify("After", *after_input.split(","))
        requires = _nspawn_ify("Requires", *requires_input.split(","))

        self._execute(
            location.next_line(),
            system_context,
            "create",
            "{}/override.conf".format(override_dir),
            textwrap.dedent(
                """\
                      [Unit]
                      Description=Container {system}: {description}{after}{requires}
                       
                      [Service]
                      TimeoutStartSec={timeout}
                      """
            ).format(
                system=system,
                description=description,
                after=after,
                requires=requires,
                timeout=timeout,
            ),
        )

        if enable:
            location.set_description("Enabling container")
            self._execute(
                location.next_line(),
                system_context,
                "symlink",
                "../systemd-nspawn@.service",
                "systemd-nspawn@{}.service".format(system),
                work_directory="{}/machines.target.wants".format(systemd_directory),
            )
