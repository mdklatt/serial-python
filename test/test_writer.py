""" Testing for the the writer.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import _path

import StringIO
import unittest

from serial.core import DelimitedWriter
from serial.core import FixedWidthWriter
from serial.core import IntType
from serial.core import ArrayType


# Utility functions.

def accept_filter(record):
    """ A filter function to accept records.

    """
    return True  # accept all records


def reject_filter(record):
    """ A filter function to reject records.

    """
    return record["B"] != 3  # reject if record["B"] == 1


def modify_filter(record):
    """ A filter function to modify records in place.

    """
    record["B"] *= 2  # modify in place
    return True


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class TabularWriterTest(unittest.TestCase):
    """ Unit testing for TabularReader classes.

    This is an abstract class and should not be called directly by any test
    runners.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.data = [
            {"A": [{"x": 1, "y": 2}], "B": 3},
            {"A": [{"x": 4, "y": 5}], "B": 6}]
        self.stream = StringIO.StringIO()
        return

    def test_write(self):
        """ Test the write() method.

        """
        map(self.writer.write, self.data)
        self.assertEqual(self.output, self.stream.getvalue())
        return

    def test_filter_accept(self):
        """ Test a filter that accepts all records.

        """
        self.writer.filter(accept_filter)
        map(self.writer.write, self.data)
        self.assertEqual(self.output, self.stream.getvalue())
        return


class DelimitedWriterTest(TabularWriterTest):
    """ Unit testing for the DelimitedWriter class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        super(DelimitedWriterTest, self).setUp()
        atype = ArrayType((("x", 0, IntType()), ("y", 1, IntType())))
        fields = (("A", (0, 2), atype), ("B", 2, IntType()))
        self.writer = DelimitedWriter(self.stream, fields, ",", "X")
        self.output = "1,2,3X4,5,6X"
        return

    def test_filter_reject(self):
        """ Test a filter that rejects a record.

        """
        self.writer.filter(accept_filter)  # test chained filters
        self.writer.filter(reject_filter)
        map(self.writer.write, self.data)
        self.assertEqual("4,5,6X", self.stream.getvalue())
        return

    def test_filter_modify(self):
        """ Test a filter that modifies records

        """
        self.writer.filter(modify_filter)
        map(self.writer.write, self.data)
        self.assertEqual("1,2,6X4,5,12X", self.stream.getvalue())
        return


class FixedWidthWriterTest(TabularWriterTest):
    """ Unit testing for the DelimitedWriter class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        super(FixedWidthWriterTest, self).setUp()
        atype = ArrayType((("x", 0, IntType("2d")), ("y", 1, IntType("2d"))))
        fields = (("A", (0, 4), atype), ("B", (4, 6), IntType("2d")))
        self.writer = FixedWidthWriter(self.stream, fields, "X")
        self.output = " 1 2 3X 4 5 6X"
        return

    def test_filter_reject(self):
        """ Test a filter that rejects a record.

        """
        self.writer.filter(accept_filter)  # test chained filters
        self.writer.filter(reject_filter)
        map(self.writer.write, self.data)
        self.assertEqual(" 4 5 6X", self.stream.getvalue())
        return

    def test_filter_modify(self):
        """ Test a filter that modifies records

        """
        self.writer.filter(modify_filter)
        map(self.writer.write, self.data)
        self.assertEqual(" 1 2 6X 4 512X", self.stream.getvalue())
        return


# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (DelimitedWriterTest, FixedWidthWriterTest)

def load_tests(loader, tests, pattern):
    """ Define a TestSuite for this module.

    This is part of the unittest API. The last two arguments are ignored. The
    _TEST_CASES global is used to determine which TestCase classes to load
    from this module.

    """
    suite = unittest.TestSuite()
    for test_case in _TEST_CASES:
        tests = loader.loadTestsFromTestCase(test_case)
        suite.addTests(tests)
    return suite


# Make the module executable.

if __name__ == "__main__":
    unittest.main()  # main() calls sys.exit()
