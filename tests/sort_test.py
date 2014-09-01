""" Testing for the the sort.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import _unittest as unittest

from io import BytesIO
from random import shuffle

from serial.core.sort import *  # tests __all__


# Mock objects to use for testing.

class _MockWriter(object):
    """ Simulate a _Writer for testing purposes.
    
    """
    def __init__(self):
        """ Initialize this object.
        
        """
        self.output = []
        self.write = self.output.append
        return


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class _SortTest(unittest.TestCase):
    """ Base class for SortReaderTest and SortWriterTest.

    This is an abstract class and should not be called directly by any test
    runners.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        values = list("abcdefghijk")
        self.sorted = tuple({"KEY": val} for val in values)
        shuffle(values)
        self.records = tuple({"KEY": val} for val in values)
        return


class SortReaderTest(_SortTest):
    """ Unit testing for the SortReader class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        super(SortReaderTest, self).setUp()
        self.reader = SortReader(iter(self.records), key="KEY")
        return

    def test_iter(self):
        """ Test the __iter__() method.

        """
        self.assertSequenceEqual(self.sorted, list(self.reader))
        return
        

class SortWriterTest(_SortTest):
    """ Unit testing for the SortWriter class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        super(SortWriterTest, self).setUp()
        self.buffer = _MockWriter()  
        return

    def test_write(self):
        """ Test the write() and close() methods.

        """
        writer = SortWriter(self.buffer, "KEY")
        for record in self.records:
            writer.write(record)
        writer.close()
        writer.close()  # test that redundant calls are a no-op
        self.assertSequenceEqual(self.sorted, self.buffer.output)
        return


# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (SortReaderTest, SortWriterTest)

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
