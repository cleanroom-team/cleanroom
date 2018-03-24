#!/usr/bin/python
"""Test for the Printer class and related functions.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.printer as printer

import random
import unittest


class TestPrinter(printer.Printer):
    """Printer class for unit testing."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super().__init__(*args, **kwargs)
        self.buffer = ''

    def _print(self, *args):
        self.buffer += ' '.join(args) + '\n'


class PrinterTest(unittest.TestCase):
    """Test for Location class of cleanroom."""

    def _verify(self, msg=None):
        msg = msg if msg is not None else self._message
        return msg in self._printer.buffer

    def _setup_printer(self, verbosity):
        """Set up printer."""
        self._message = "Message " + str(random.randint(0, 1000000))
        self.tearDown()
        self._printer = TestPrinter(verbosity)

    def tearDown(self):
        """Tear down method."""
        printer.Printer._instance = None

    def _test_message(self, op, global_verbosity, **kwargs):
        self._setup_printer(global_verbosity)
        op(self._message, **kwargs)
        self.assertTrue(self._verify())

    def _test_no_output(self, op, global_verbosity, **kwargs):
        self._setup_printer(global_verbosity)
        op(self._message, **kwargs)
        self.assertEqual(self._printer.buffer, '')

    # Verbosity: 0
    def test_h1_v0(self):
        """Test h1 at verbosity 0."""
        self._test_message(printer.h1, 0)
        self.assertTrue(self._verify('======================'))

    def test_h1v1_v0(self):
        """Test h1 (v1) at verbosity 0."""
        self._test_no_output(printer.h1, 0, verbosity=1)

    def test_h1v2_v0(self):
        """Test h1 (v2) at verbosity 0."""
        self._test_no_output(printer.h1, 0, verbosity=2)

    def test_h1v3_v0(self):
        """Test h1 (v3) at verbosity 0."""
        self._test_no_output(printer.h1, 0, verbosity=3)

    def test_h1v4_v0(self):
        """Test h1 (v4) at verbosity 0."""
        self._test_no_output(printer.h1, 0, verbosity=4)

    def test_h1v5_v0(self):
        """Test h1 (v5) at verbosity 0."""
        self._test_no_output(printer.h1, 0, verbosity=5)

    def test_h2_v0(self):
        """Test h2 at verbosity 0."""
        self._test_message(printer.h2, 0)
        self.assertTrue(self._verify('*****'))

    def test_h2v1_v0(self):
        """Test h2 (v1) at verbosity 0."""
        self._test_no_output(printer.h2, 0, verbosity=1)

    def test_h2v2_v0(self):
        """Test h2 (v2) at verbosity 0."""
        self._test_no_output(printer.h2, 0, verbosity=2)

    def test_h2v3_v0(self):
        """Test h2 (v3) at verbosity 0."""
        self._test_no_output(printer.h2, 0, verbosity=3)

    def test_h2v4_v0(self):
        """Test h2 (v4) at verbosity 0."""
        self._test_no_output(printer.h2, 0, verbosity=4)

    def test_h2v5_v0(self):
        """Test h2 (v5) at verbosity 0."""
        self._test_no_output(printer.h2, 0, verbosity=5)

    def test_h3_v0(self):
        """Test h3 at verbosity 0."""
        self._test_message(printer.h3, 0)
        self.assertTrue(self._verify('*****'))

    def test_h3v1_v0(self):
        """Test h3 (v1) at verbosity 0."""
        self._test_no_output(printer.h3, 0, verbosity=1)

    def test_h3v2_v0(self):
        """Test h3 (v2) at verbosity 0."""
        self._test_no_output(printer.h3, 0, verbosity=2)

    def test_h3v3_v0(self):
        """Test h3 (v3) at verbosity 0."""
        self._test_no_output(printer.h3, 0, verbosity=3)

    def test_h3v4_v0(self):
        """Test h3 (v4) at verbosity 0."""
        self._test_no_output(printer.h3, 0, verbosity=4)

    def test_h3v5_v0(self):
        """Test h3 (v5) at verbosity 0."""
        self._test_no_output(printer.h3, 0, verbosity=5)

    def test_error_v0(self):
        """Test error at verbosity 0."""
        self._test_message(printer.error, 0)
        self.assertTrue(self._verify('ERROR'))

    def test_errorv1_v0(self):
        """Test error (v1) at verbosity 0."""
        self._test_no_output(printer.error, 0, verbosity=1)

    def test_errorv2_v0(self):
        """Test error (v2) at verbosity 0."""
        self._test_no_output(printer.error, 0, verbosity=2)

    def test_errorv3_v0(self):
        """Test error (v3) at verbosity 0."""
        self._test_no_output(printer.error, 0, verbosity=3)

    def test_errorv4_v0(self):
        """Test error (v4) at verbosity 0."""
        self._test_no_output(printer.error, 0, verbosity=4)

    def test_errorv5_v0(self):
        """Test error (v5) at verbosity 0."""
        self._test_no_output(printer.error, 0, verbosity=5)

    def test_warn_v0(self):
        """Test warn at verbosity 0."""
        self._test_message(printer.warn, 0)
        self.assertTrue(self._verify('warn'))

    def test_warnv1_v0(self):
        """Test warn (v1) at verbosity 0."""
        self._test_no_output(printer.warn, 0, verbosity=1)

    def test_warnv2_v0(self):
        """Test warn (v2) at verbosity 0."""
        self._test_no_output(printer.warn, 0, verbosity=2)

    def test_warnv3_v0(self):
        """Test warn (v3) at verbosity 0."""
        self._test_no_output(printer.warn, 0, verbosity=3)

    def test_warnv4_v0(self):
        """Test warn (v4) at verbosity 0."""
        self._test_no_output(printer.warn, 0, verbosity=4)

    def test_warnv5_v0(self):
        """Test warn (v5) at verbosity 0."""
        self._test_no_output(printer.warn, 0, verbosity=5)

    def test_success_v0(self):
        """Test success at verbosity 0."""
        self._test_message(printer.success, 0)
        self.assertTrue(self._verify('OK'))

    def test_successv1_v0(self):
        """Test success (v1) at verbosity 0."""
        self._test_no_output(printer.success, 0, verbosity=1)

    def test_successv2_v0(self):
        """Test success (v2) at verbosity 0."""
        self._test_no_output(printer.success, 0, verbosity=2)

    def test_successv3_v0(self):
        """Test success (v3) at verbosity 0."""
        self._test_no_output(printer.success, 0, verbosity=3)

    def test_successv4_v0(self):
        """Test success (v4) at verbosity 0."""
        self._test_no_output(printer.success, 0, verbosity=4)

    def test_successv5_v0(self):
        """Test success (v5) at verbosity 0."""
        self._test_no_output(printer.success, 0, verbosity=5)

    def test_fail_ignore_v0(self):
        """Test success at verbosity 0."""
        self._test_message(printer.fail, 0, ignore=True)
        self.assertTrue(self._verify('fail'))

    def test_fail_ignorev1_v0(self):
        """Test fail ignore (v1) at verbosity 0."""
        self._test_no_output(printer.fail, 0, ignore=True, verbosity=1)

    def test_fail_ignorev2_v0(self):
        """Test fail ignore (v2) at verbosity 0."""
        self._test_no_output(printer.fail, 0, ignore=True, verbosity=2)

    def test_fail_ignorev3_v0(self):
        """Test fail ignore (v3) at verbosity 0."""
        self._test_no_output(printer.fail, 0, ignore=True, verbosity=3)

    def test_fail_ignorev4_v0(self):
        """Test fail ignore (v4) at verbosity 0."""
        self._test_no_output(printer.fail, 0, ignore=True, verbosity=4)

    def test_fail_ignorev5_v0(self):
        """Test fail ignore (v5) at verbosity 0."""
        self._test_no_output(printer.fail, 0, ignore=True, verbosity=5)

    def test_fail_v0(self):
        """Test success at verbosity 0."""
        self._test_message(printer.fail, 0, force_exit=False)
        self.assertTrue(self._verify('FAIL'))

    def test_failv1_v0(self):
        """Test fail ignore (v1) at verbosity 0."""
        self._test_no_output(printer.fail, 0, force_exit=False, verbosity=1)

    def test_failv2_v0(self):
        """Test fail ignore (v2) at verbosity 0."""
        self._test_no_output(printer.fail, 0, force_exit=False, verbosity=2)

    def test_failv3_v0(self):
        """Test fail ignore (v3) at verbosity 0."""
        self._test_no_output(printer.fail, 0, force_exit=False, verbosity=3)

    def test_failv4_v0(self):
        """Test fail ignore (v4) at verbosity 0."""
        self._test_no_output(printer.fail, 0, force_exit=False, verbosity=4)

    def test_failv5_v0(self):
        """Test fail (v5) at verbosity 0."""
        self._test_no_output(printer.fail, 0, force_exit=False, verbosity=5)

    def test_msg_v0(self):
        """Test msg at verbosity 0."""
        self._test_message(printer.msg, 0)
        self.assertFalse(self._verify('     '))

    def test_verbose_v0(self):
        """Test verbose at verbosity 0."""
        self._test_no_output(printer.verbose, 0)

    def test_info_v0(self):
        """Test info at verbosity 0."""
        self._test_no_output(printer.info, 0)

    def test_debug_v0(self):
        """Test debug at verbosity 0."""
        self._test_no_output(printer.debug, 0)

    def test_trace_v0(self):
        """Test trace at verbosity 0."""
        self._test_no_output(printer.trace, 0)

    # Verbosity: 1
    def test_h1_v1(self):
        """Test h1 at verbosity 1."""
        self._test_message(printer.h1, 1)
        self.assertTrue(self._verify('======================'))

    def test_h2_v1(self):
        """Test h2 at verbosity 1."""
        self._test_message(printer.h2, 1)
        self.assertTrue(self._verify('*****'))

    def test_h3_v1(self):
        """Test h3 at verbosity 1."""
        self._test_message(printer.h3, 1)
        self.assertTrue(self._verify('*****'))

    def test_error_v1(self):
        """Test error at verbosity 1."""
        self._test_message(printer.error, 1)
        self.assertTrue(self._verify('ERROR'))

    def test_warn_v1(self):
        """Test warn at verbosity 1."""
        self._test_message(printer.warn, 1)
        self.assertTrue(self._verify('warn'))

    def test_success_v1(self):
        """Test success at verbosity 1."""
        self._test_message(printer.success, 1)
        self.assertTrue(self._verify('OK'))

    def test_fail_ignore_v1(self):
        """Test success at verbosity 1."""
        self._test_message(printer.fail, 1, ignore=True)
        self.assertTrue(self._verify('fail'))

    def test_fail_v1(self):
        """Test success at verbosity 1."""
        self._test_message(printer.fail, 1, force_exit=False)
        self.assertTrue(self._verify('FAIL'))

    def test_msg_v1(self):
        """Test msg at verbosity 1."""
        self._test_message(printer.msg, 1)
        self.assertTrue(self._verify('     '))

    def test_verbose_v1(self):
        """Test verbose at verbosity 1."""
        self._test_message(printer.verbose, 1)
        self.assertTrue(self._verify('     '))

    def test_info_v1(self):
        """Test info at verbosity 1."""
        self._test_no_output(printer.info, 1)

    def test_debug_v1(self):
        """Test debug at verbosity 1."""
        self._test_no_output(printer.debug, 1)

    def test_trace_v1(self):
        """Test trace at verbosity 1."""
        self._test_no_output(printer.trace, 1)

    # Verbosity: 2
    def test_h1_v2(self):
        """Test h1 at verbosity 2."""
        self._test_message(printer.h1, 2)
        self.assertTrue(self._verify('======================'))

    def test_h2_v2(self):
        """Test h2 at verbosity 2."""
        self._test_message(printer.h2, 2)
        self.assertTrue(self._verify('*****'))

    def test_h3_v2(self):
        """Test h3 at verbosity 2."""
        self._test_message(printer.h3, 2)
        self.assertTrue(self._verify('*****'))

    def test_error_v2(self):
        """Test error at verbosity 2."""
        self._test_message(printer.error, 2)
        self.assertTrue(self._verify('ERROR'))

    def test_warn_v2(self):
        """Test warn at verbosity 2."""
        self._test_message(printer.warn, 2)
        self.assertTrue(self._verify('warn'))

    def test_success_v2(self):
        """Test success at verbosity 2."""
        self._test_message(printer.success, 2)
        self.assertTrue(self._verify('OK'))

    def test_fail_ignore_v2(self):
        """Test success at verbosity 2."""
        self._test_message(printer.fail, 2, ignore=True)
        self.assertTrue(self._verify('fail'))

    def test_fail_v2(self):
        """Test success at verbosity 2."""
        self._test_message(printer.fail, 2, force_exit=False)
        self.assertTrue(self._verify('FAIL'))

    def test_msg_v2(self):
        """Test msg at verbosity 2."""
        self._test_message(printer.msg, 2)
        self.assertTrue(self._verify('     '))

    def test_verbose_v2(self):
        """Test verbose at verbosity 2."""
        self._test_message(printer.verbose, 2)
        self.assertTrue(self._verify('     '))

    def test_info_v2(self):
        """Test info at verbosity 2."""
        self._test_message(printer.info, 2)
        self.assertTrue(self._verify('.....'))

    def test_debug_v2(self):
        """Test debug at verbosity 2."""
        self._test_no_output(printer.debug, 2)

    def test_trace_v2(self):
        """Test trace at verbosity 2."""
        self._test_no_output(printer.trace, 2)

    # Verbosity: 3
    def test_h1_v3(self):
        """Test h1 at verbosity 3."""
        self._test_message(printer.h1, 3)
        self.assertTrue(self._verify('======================'))

    def test_h2_v3(self):
        """Test h2 at verbosity 3."""
        self._test_message(printer.h2, 3)
        self.assertTrue(self._verify('*****'))

    def test_h3_v3(self):
        """Test h3 at verbosity 3."""
        self._test_message(printer.h3, 3)
        self.assertTrue(self._verify('*****'))

    def test_error_v3(self):
        """Test error at verbosity 3."""
        self._test_message(printer.error, 3)
        self.assertTrue(self._verify('ERROR'))

    def test_warn_v3(self):
        """Test warn at verbosity 3."""
        self._test_message(printer.warn, 3)
        self.assertTrue(self._verify('warn'))

    def test_success_v3(self):
        """Test success at verbosity 3."""
        self._test_message(printer.success, 3)
        self.assertTrue(self._verify('OK'))

    def test_fail_ignore_v3(self):
        """Test success at verbosity 3."""
        self._test_message(printer.fail, 3, ignore=True)
        self.assertTrue(self._verify('fail'))

    def test_fail_v3(self):
        """Test success at verbosity 3."""
        self._test_message(printer.fail, 3, force_exit=False)
        self.assertTrue(self._verify('FAIL'))

    def test_msg_v3(self):
        """Test msg at verbosity 3."""
        self._test_message(printer.msg, 3)
        self.assertTrue(self._verify('     '))

    def test_verbose_v3(self):
        """Test verbose at verbosity 3."""
        self._test_message(printer.verbose, 3)
        self.assertTrue(self._verify('     '))

    def test_info_v3(self):
        """Test info at verbosity 3."""
        self._test_message(printer.info, 3)
        self.assertTrue(self._verify('.....'))

    def test_debug_v3(self):
        """Test debug at verbosity 3."""
        self._test_message(printer.debug, 3)
        self.assertTrue(self._verify('-----'))

    def test_trace_v3(self):
        """Test trace at verbosity 3."""
        self._test_no_output(printer.trace, 3)

    # Verbosity: 4
    def test_h1_v4(self):
        """Test h1 at verbosity 4."""
        self._test_message(printer.h1, 4)
        self.assertTrue(self._verify('======================'))

    def test_h2_v4(self):
        """Test h2 at verbosity 4."""
        self._test_message(printer.h2, 4)
        self.assertTrue(self._verify('*****'))

    def test_h3_v4(self):
        """Test h3 at verbosity 4."""
        self._test_message(printer.h3, 4)
        self.assertTrue(self._verify('*****'))

    def test_error_v4(self):
        """Test error at verbosity 4."""
        self._test_message(printer.error, 4)
        self.assertTrue(self._verify('ERROR'))

    def test_warn_v4(self):
        """Test warn at verbosity 4."""
        self._test_message(printer.warn, 4)
        self.assertTrue(self._verify('warn'))

    def test_success_v4(self):
        """Test success at verbosity 4."""
        self._test_message(printer.success, 4)
        self.assertTrue(self._verify('OK'))

    def test_fail_ignore_v4(self):
        """Test success at verbosity 4."""
        self._test_message(printer.fail, 4, ignore=True)
        self.assertTrue(self._verify('fail'))

    def test_fail_v4(self):
        """Test success at verbosity 4."""
        self._test_message(printer.fail, 4, force_exit=False)
        self.assertTrue(self._verify('FAIL'))

    def test_msg_v4(self):
        """Test msg at verbosity 4."""
        self._test_message(printer.msg, 4)
        self.assertTrue(self._verify('     '))

    def test_verbose_v4(self):
        """Test verbose at verbosity 4."""
        self._test_message(printer.verbose, 4)
        self.assertTrue(self._verify('     '))

    def test_info_v4(self):
        """Test info at verbosity 4."""
        self._test_message(printer.info, 4)
        self.assertTrue(self._verify('.....'))

    def test_debug_v4(self):
        """Test debug at verbosity 4."""
        self._test_message(printer.debug, 4)
        self.assertTrue(self._verify('-----'))

    def test_trace_v4(self):
        """Test trace at verbosity 4."""
        self._test_message(printer.trace, 4)
        self.assertTrue(self._verify('+++++'))

    # Verbosity: 5
    def test_h1_v5(self):
        """Test h1 at verbosity 5."""
        self._test_message(printer.h1, 5)
        self.assertTrue(self._verify('======================'))

    def test_h2_v5(self):
        """Test h2 at verbosity 5."""
        self._test_message(printer.h2, 5)
        self.assertTrue(self._verify('*****'))

    def test_h3_v5(self):
        """Test h3 at verbosity 5."""
        self._test_message(printer.h3, 5)
        self.assertTrue(self._verify('*****'))

    def test_error_v5(self):
        """Test error at verbosity 5."""
        self._test_message(printer.error, 5)
        self.assertTrue(self._verify('ERROR'))

    def test_warn_v5(self):
        """Test warn at verbosity 5."""
        self._test_message(printer.warn, 5)
        self.assertTrue(self._verify('warn'))

    def test_success_v5(self):
        """Test success at verbosity 5."""
        self._test_message(printer.success, 5)
        self.assertTrue(self._verify('OK'))

    def test_fail_ignore_v5(self):
        """Test success at verbosity 5."""
        self._test_message(printer.fail, 5, ignore=True)
        self.assertTrue(self._verify('fail'))

    def test_fail_v5(self):
        """Test success at verbosity 5."""
        self._test_message(printer.fail, 5, force_exit=False)
        self.assertTrue(self._verify('FAIL'))

    def test_msg_v5(self):
        """Test msg at verbosity 5."""
        self._test_message(printer.msg, 5)
        self.assertTrue(self._verify('     '))

    def test_verbose_v5(self):
        """Test verbose at verbosity 5."""
        self._test_message(printer.verbose, 5)
        self.assertTrue(self._verify('     '))

    def test_info_v5(self):
        """Test info at verbosity 5."""
        self._test_message(printer.info, 5)
        self.assertTrue(self._verify('.....'))

    def test_debug_v5(self):
        """Test debug at verbosity 5."""
        self._test_message(printer.debug, 5)
        self.assertTrue(self._verify('-----'))

    def test_trace_v5(self):
        """Test trace at verbosity 5."""
        self._test_message(printer.trace, 5)
        self.assertTrue(self._verify('+++++'))


if __name__ == '__main__':
    random.seed()
    unittest.main()
