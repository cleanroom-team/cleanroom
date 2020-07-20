# -*- coding: utf-8 -*-
"""Pretty-print output of cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from io import StringIO
from os import getenv
import sys
import typing


def h1(*args: str, **kwargs: typing.Any) -> None:
    """Print main headline."""
    Printer.instance().h1(*args, **kwargs)


def h2(*args: str, **kwargs: typing.Any) -> None:
    """Print sub headline."""
    Printer.instance().h2(*args, **kwargs)


def h3(*args: str, **kwargs: typing.Any) -> None:
    """Print sub-sub headline."""
    Printer.instance().h3(*args, **kwargs)


def error(*args: str, **kwargs: typing.Any) -> None:
    """Print error message."""
    Printer.instance().error(*args, **kwargs)


def warn(*args: str, **kwargs: typing.Any) -> None:
    """Print warning message."""
    Printer.instance().warn(*args, **kwargs)


def success(*args: str, **kwargs: typing.Any) -> None:
    """Print success message."""
    Printer.instance().success(*args, **kwargs)


def fail(*args: str, **kwargs: typing.Any) -> None:
    """Print fail message."""
    Printer.instance().fail(*args, **kwargs)


def msg(*args: str) -> None:
    """Print arguments."""
    Printer.instance().msg(*args)


def verbose(*args: str) -> None:
    """Print if verbose is set."""
    Printer.instance().verbose(*args)


def info(*args: str) -> None:
    """Print even more verbose."""
    Printer.instance().info(*args)


def debug(*args: str) -> None:
    """Print if debug is set."""
    Printer.instance().debug(*args)


def trace(*args: str) -> None:
    """Print trace messsages."""
    Printer.instance().trace(*args)


def none(*args: str) -> None:
    """Do nothing."""
    pass


def _ansi_fy(seq: str) -> str:
    """Use ANSI color codes if possible.

    Use ANSI color codes if possible and strip them out if not.
    """
    if sys.stdout.isatty():
        return seq
    return ""


class Printer:
    """Pretty-print output.

    A Printer will be set up by the cleanroom executable and
    passed on to the cleanroom module.

    The module will then use this Printer object for all its
    output needs.
    """

    _instance = None

    @staticmethod
    def instance() -> "Printer":
        """Get the main printer instance."""
        if Printer._instance is None:
            verbosity = int(getenv("CLRM_LOG_VERBOSITY", 0))
            Printer._instance = Printer(verbosity=verbosity)
        return Printer._instance

    def __init__(self, verbosity: int = 0) -> None:
        """Constructor."""
        self._verbose = 0
        self._prefix = ""

        self.set_verbosity(verbosity)

        self._ansi_reset = _ansi_fy("\033[0m")
        self._h_prefix = _ansi_fy("\033[1;31m")
        self._h1_suffix = _ansi_fy("\033[0m\033[1;37m")
        self._error_prefix = _ansi_fy("\033[1;31m")
        self._warn_prefix = _ansi_fy("\033[1;33m")
        self._ok_prefix = _ansi_fy("\033[1;7;32m")
        self._ok_suffix = _ansi_fy("\033[0;32m")

        self._ig_fail_prefix = _ansi_fy("\033[1;7;33m")
        self._ig_fail_suffix = _ansi_fy("\033[0;33m")
        self._fail_prefix = _ansi_fy("\033[1;7;31m")
        self._fail_suffix = _ansi_fy("\033[0;31m")
        self._extra_prefix = _ansi_fy("\033[1;36m")
        self._extra_suffix = _ansi_fy("\033[0;m\033[2;m")

        self._buffer = ""

        Printer._instance = self

    def flush(self) -> None:
        buf = self._buffer
        self._buffer = ""

        if buf:
            print(">>>>>> Flushing buffer:")
            print(buf)
            print(">>>>>> End of Buffer <<<<<<")
        else:
            print(">>>>>> No buffered output <<<<<<")

    def set_verbosity(self, verbosity: int) -> None:
        """Set the verbosity."""
        self._verbose = verbosity
        self._prefix = "      " if verbosity > 0 else ""

    @staticmethod
    def show_verbosity_level() -> None:
        if Printer.instance()._print_at_verbosity_level(3):
            verbose("Verbose output enabled.")
            info("Info output enabled.")
            debug("Debug output enabled.")
            trace("Trace output enabled.")

    def _print_to_buffer(self, *args: str) -> None:
        buf = StringIO()
        print(*args, file=buf)
        self._buffer += buf.getvalue()

    def _print_impl(self, *args: str, **kwargs: typing.Any) -> None:
        print(*args, **kwargs)

    def _print(self, *args: str, verbosity: int = 0) -> None:
        self._print_to_buffer(*args)

        if self._print_at_verbosity_level(verbosity):
            self._print_impl(*args)

    def _print_at_verbosity_level(self, verbosity: int) -> bool:
        return verbosity <= self._verbose

    def h1(self, *args: str, verbosity: int = 0) -> None:
        """Print big headline."""
        intro = "\n\n{}============================================{}".format(
            self._h1_suffix, self._ansi_reset
        )
        prefix = "{}== ".format(self._h1_suffix)
        postfix = "{}============================================{}".format(
            self._h1_suffix, self._ansi_reset
        )
        self._print(intro, verbosity=verbosity)
        self._print(prefix, *args, self._ansi_reset, verbosity=verbosity)
        self._print(postfix, verbosity=verbosity)
        self._print(verbosity=verbosity)
        self._buffer = ""

    def h2(self, *args: str, verbosity: int = 0) -> None:
        """Print a headline."""
        intro = "\n{}******{}".format(self._h_prefix, self._h1_suffix)
        self._print(intro, *args, self._ansi_reset, verbosity=verbosity)

    def h3(self, *args: str, verbosity: int = 0) -> None:
        """Print a subheading."""
        intro = "\n{}******{}".format(self._h_prefix, self._ansi_reset)
        self._print(intro, *args, verbosity=verbosity)

    def error(self, *args: str, verbosity: int = 0) -> None:
        """Print error message."""
        intro = "{}ERROR:".format(self._error_prefix)
        self._print(intro, *args, self._ansi_reset, verbosity=verbosity)

    def warn(self, *args: str, verbosity: int = 0) -> None:
        """Print warning message."""
        intro = "{}warn: ".format(self._warn_prefix)
        self._print(intro, *args, self._ansi_reset, verbosity=verbosity)

    def success(self, *args: str, verbosity: int = 0) -> None:
        """Print success message."""
        intro = "{}  OK  {}".format(self._ok_prefix, self._ok_suffix)
        self._print(intro, *args, self._ansi_reset, verbosity=verbosity)
        self._buffer = ""

    def fail(
        self,
        *args: str,
        verbosity: int = 0,
        force_exit: bool = True,
        ignore: bool = False
    ) -> None:
        """Print fail message."""
        if ignore:
            intro = "{} fail {}".format(self._ig_fail_prefix, self._ig_fail_suffix)
            self._print(
                intro, *args, "(ignored)", self._ansi_reset, verbosity=verbosity
            )
        else:
            intro = "{} FAIL {}".format(self._fail_prefix, self._fail_suffix)
            self._print(intro, *args, self._ansi_reset, verbosity=verbosity)
            if force_exit:
                sys.exit(1)

    def msg(self, *args: str) -> None:
        """Print arguments."""
        self._print(self._prefix, *args, verbosity=0)

    def verbose(self, *args: str) -> None:
        """Print if verbose is set."""
        self._print(self._prefix, *args, verbosity=1)

    def info(self, *args: str) -> None:
        """Print even more verbose."""
        intro = "{}......{}".format(self._extra_prefix, self._extra_suffix)
        self._print(intro, *args, self._ansi_reset, verbosity=2)

    def debug(self, *args: str) -> None:
        """Print if debug is set."""
        intro = "{}------{}".format(self._extra_prefix, self._extra_suffix)
        self._print(intro, *args, self._ansi_reset, verbosity=3)

    def trace(self, *args: str) -> None:
        """Print trace messsages."""
        intro = "{}++++++{}".format(self._extra_prefix, self._extra_suffix)
        self._print(intro, *args, self._ansi_reset, verbosity=4)
