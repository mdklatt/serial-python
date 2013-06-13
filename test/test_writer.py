""" Testing for the the writer.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
from StringIO import StringIO

import _path
import _unittest as unittest

from serial.core import DelimitedWriter
from serial.core import FixedWidthWriter
from serial.core import ArrayType
from serial.core import IntType
from serial.core import StringType


# Utility functions.

def reject_filter(record):
    """ A filter function to reject records.

    """
    return record if record["int"] != 123 else None


def modify_filter(record):
    """ A filter function to modify records.

    """
    record["int"] *= 2
    return record


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class _TabularWriterTest(unittest.TestCase):
    """ Unit testing for _TabularReader classes.

    This is an abstract class and should not be called directly by any test
    runners.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.records = (
            {"arr": [{"x": "abc", "y": "def"}], "int": 123},
            {"arr": [{"x": "ghi", "y": "jkl"}], "int": 456})
        self.stream = StringIO()
        return

    def test_write(self):
        """ Test the write() method.

        """
        for record in self.records:
            self.writer.write(record)
        self.assertEqual(self.data, self.stream.getvalue())
        return

    def test_dump(self):
        """ Test the dump() method.

        """
        self.writer.dump(self.records)
        self.assertEqual(self.data, self.stream.getvalue())
        return


class DelimitedWriterTest(_TabularWriterTest):
    """ Unit testing for the DelimitedWriter class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        array_fields = (
            ("x", 0, StringType()), 
            ("y", 1, StringType()))
        fields = (
            ("arr", (0, 2), ArrayType(array_fields)), 
            ("int", 2, IntType()))
        super(DelimitedWriterTest, self).setUp()
        self.writer = DelimitedWriter(self.stream, fields, ",", "X")
        self.data = "abc,def,123Xghi,jkl,456X"
        return

    def test_filter(self):
        """ Test the filter() method.

        """
        self.writer.filter(reject_filter)
        self.writer.filter(modify_filter)
        self.data = "ghi,jkl,912X"
        self.test_dump()
        return


class FixedWidthWriterTest(_TabularWriterTest):
    """ Unit testing for the DelimitedWriter class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        array_fields = (
            ("x", (0, 3), StringType("3s")), 
            ("y", (3, 6), StringType("3s")))
        fields = (
            ("arr", (0, 6), ArrayType(array_fields)), 
            ("int", (6, 9), IntType("3d")))
        super(FixedWidthWriterTest, self).setUp()
        self.writer = FixedWidthWriter(self.stream, fields, "X")
        self.data = "abcdef123Xghijkl456X"
        return

    def test_filter(self):
        """ Test a filter that modifies records

        """
        self.writer.filter(reject_filter)
        self.writer.filter(modify_filter)
        self.data = "ghijkl912X"
        self.test_dump()
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
