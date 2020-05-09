#!/usr/bin/python
"""Test for the Printer class and related functions.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import pytest  # type: ignore
import random
import typing

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import cleanroom.printer


class DummyPrinter(cleanroom.printer.Printer):
    """Printer class for unit testing."""

    def __init__(self, *args, **kwargs) -> None:
        """Constructor."""
        super().__init__(*args, **kwargs)
        self.buffer = ""

    def _print_impl(self, *args: str, **kwargs: typing.Any) -> None:
        self.buffer += " ".join(args) + "\n"


@pytest.fixture()
def printer() -> DummyPrinter:
    """Return a printer."""
    return DummyPrinter(verbosity=0)


def _test_message(
    printer: DummyPrinter,
    printer_verbosity: int,
    op: typing.Callable,
    has_output: bool,
    extras: typing.Tuple[str, ...] = (),
    **kwargs: typing.Any
) -> None:
    printer.set_verbosity(printer_verbosity)
    message = "Message " + str(random.randint(0, 1000000))
    op(message, **kwargs)
    if has_output:
        assert message in printer.buffer
        for extra in extras:
            assert extra in printer.buffer
    else:
        assert printer.buffer == ""


@pytest.mark.parametrize("printer_verbosity", [0, 1, 2, 3, 4, 5])
@pytest.mark.parametrize("message_verbosity", [0, 1, 2, 3, 4, 5])
def test_printing_h1(
    printer: DummyPrinter, printer_verbosity: int, message_verbosity: int
) -> None:
    """Test printing."""
    _test_message(
        printer,
        printer_verbosity,
        printer.h1,
        printer_verbosity >= message_verbosity,
        ("=====================",),
        verbosity=message_verbosity,
    )


@pytest.mark.parametrize("printer_verbosity", [0, 1, 2, 3, 4, 5])
@pytest.mark.parametrize("message_verbosity", [0, 1, 2, 3, 4, 5])
def test_printing_h2(
    printer: DummyPrinter, printer_verbosity: int, message_verbosity: int
) -> None:
    """Test printing."""
    _test_message(
        printer,
        printer_verbosity,
        printer.h2,
        printer_verbosity >= message_verbosity,
        ("*****",),
        verbosity=message_verbosity,
    )


@pytest.mark.parametrize("printer_verbosity", [0, 1, 2, 3, 4, 5])
@pytest.mark.parametrize("message_verbosity", [0, 1, 2, 3, 4, 5])
def test_printing_h3(
    printer: DummyPrinter, printer_verbosity: int, message_verbosity: int
) -> None:
    """Test printing."""
    _test_message(
        printer,
        printer_verbosity,
        printer.h3,
        printer_verbosity >= message_verbosity,
        ("*****",),
        verbosity=message_verbosity,
    )


@pytest.mark.parametrize("printer_verbosity", [0, 1, 2, 3, 4, 5])
@pytest.mark.parametrize("message_verbosity", [0, 1, 2, 3, 4, 5])
def test_printing_error(
    printer: DummyPrinter, printer_verbosity: int, message_verbosity: int
) -> None:
    """Test printing."""
    _test_message(
        printer,
        printer_verbosity,
        printer.error,
        printer_verbosity >= message_verbosity,
        ("ERROR",),
        verbosity=message_verbosity,
    )


@pytest.mark.parametrize("printer_verbosity", [0, 1, 2, 3, 4, 5])
@pytest.mark.parametrize("message_verbosity", [0, 1, 2, 3, 4, 5])
def test_printing_warn(
    printer: DummyPrinter, printer_verbosity: int, message_verbosity: int
) -> None:
    """Test printing."""
    _test_message(
        printer,
        printer_verbosity,
        printer.warn,
        printer_verbosity >= message_verbosity,
        ("warn",),
        verbosity=message_verbosity,
    )


@pytest.mark.parametrize("printer_verbosity", [0, 1, 2, 3, 4, 5])
@pytest.mark.parametrize("message_verbosity", [0, 1, 2, 3, 4, 5])
def test_printing_success(
    printer: DummyPrinter, printer_verbosity: int, message_verbosity: int
) -> None:
    """Test printing."""
    _test_message(
        printer,
        printer_verbosity,
        printer.success,
        printer_verbosity >= message_verbosity,
        ("OK",),
        verbosity=message_verbosity,
    )


@pytest.mark.parametrize("printer_verbosity", [0, 1, 2, 3, 4, 5])
@pytest.mark.parametrize("message_verbosity", [0, 1, 2, 3, 4, 5])
def test_printing_fail_ignore(
    printer: DummyPrinter, printer_verbosity: int, message_verbosity: int
) -> None:
    """Test printing."""
    _test_message(
        printer,
        printer_verbosity,
        printer.fail,
        printer_verbosity >= message_verbosity,
        ("fail",),
        verbosity=message_verbosity,
        ignore=True,
    )


@pytest.mark.parametrize("printer_verbosity", [0, 1, 2, 3, 4, 5])
@pytest.mark.parametrize("message_verbosity", [0, 1, 2, 3, 4, 5])
def test_printing_fail(
    printer: DummyPrinter, printer_verbosity: int, message_verbosity: int
) -> None:
    """Test printing."""
    _test_message(
        printer,
        printer_verbosity,
        printer.fail,
        printer_verbosity >= message_verbosity,
        ("FAIL",),
        verbosity=message_verbosity,
        force_exit=False,
    )


@pytest.mark.parametrize("printer_verbosity", [0, 1, 2, 3, 4, 5])
def test_printing_msg(printer: DummyPrinter, printer_verbosity: int) -> None:
    """Test printing."""
    _test_message(printer, printer_verbosity, printer.msg, True)


@pytest.mark.parametrize("printer_verbosity", [0, 1, 2, 3, 4, 5])
def test_printing_verbose(printer: DummyPrinter, printer_verbosity: int) -> None:
    """Test printing."""
    _test_message(printer, printer_verbosity, printer.verbose, printer_verbosity >= 1)


@pytest.mark.parametrize("printer_verbosity", [0, 1, 2, 3, 4, 5])
def test_printing_info(printer: DummyPrinter, printer_verbosity: int) -> None:
    """Test printing."""
    _test_message(
        printer, printer_verbosity, printer.info, printer_verbosity >= 2, (".....",)
    )


@pytest.mark.parametrize("printer_verbosity", [0, 1, 2, 3, 4, 5])
def test_printing_debug(printer: DummyPrinter, printer_verbosity: int) -> None:
    """Test printing."""
    _test_message(
        printer, printer_verbosity, printer.debug, printer_verbosity >= 3, ("-----",)
    )


@pytest.mark.parametrize("printer_verbosity", [0, 1, 2, 3, 4, 5])
def test_printing_trace(printer: DummyPrinter, printer_verbosity: int) -> None:
    """Test printing."""
    _test_message(
        printer, printer_verbosity, printer.trace, printer_verbosity >= 4, ("+++++",)
    )
