""" Testing for the the dtype.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
from StringIO import StringIO

import _path
import _unittest as unittest

from serial.core import DelimitedReader
from serial.core import FixedWidthReader
from serial.core import IntType
from serial.core import StringType
from serial.core import ArrayType


# Utility functions.

def reject_filter(record):
    """ A filter function to reject records.

    """
    return record if record["int"] != 123 else None


def modify_filter(record):
    """ A filter function to modify records.

    """
    # Input filters can safely modify record.
    record["int"] *= 10 
    return record


def stop_filter(record):
    """ A filter function to stop iteration.

    """
    if record["int"] == 456:
        raise StopIteration
    return record


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class _TabularReaderTest(unittest.TestCase):
    """ Unit testing for _TabularReader classes.

    This is an abstract class and should not be called directly by any test
    runners.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.records = [
            {"arr": [{"x": "abc", "y": "def"}], "int": 123},
            {"arr": [{"x": "ghi", "y": "jkl"}], "int": 456}]
        self.stream = StringIO(self.data)
        return

    def test_next(self):
        """ Test the next() method.

        """
        self.assertEqual(self.records[0], self.reader.next())
        return

    def test_iter(self):
        """ Test the __iter__() method.

        """
        self.assertSequenceEqual(self.records, list(self.reader))
        return

    def test_filter(self):
        """ Test the filter method().

        """
        self.records = self.records[1:]
        self.records[0]["int"] = 4560
        self.reader.filter(reject_filter)
        self.reader.filter(modify_filter)
        self.test_iter()
        return

    def test_filter_stop(self):
        """ Test a filter that stops iteration.

        """
        self.records = self.records[:1]
        self.reader.filter(stop_filter)
        self.test_iter()
        return


class DelimitedReaderTest(_TabularReaderTest):
    """ Unit testing for the DelimitedReader class.

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
        self.data = "abc, def, 123\nghi, jkl, 456\n"
        super(DelimitedReaderTest, self).setUp()
        self.reader = DelimitedReader(self.stream, fields, ",")
        return


class FixedWidthReaderTest(_TabularReaderTest):
    """ Unit testing for the FixedWidthReader class.

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
        self.data = "abcdef123\nghijkl456\n"
        super(FixedWidthReaderTest, self).setUp()
        self.reader = FixedWidthReader(self.stream, fields)
        return


# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (DelimitedReaderTest, FixedWidthReaderTest)

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
