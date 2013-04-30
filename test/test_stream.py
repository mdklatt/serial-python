""" Testing for the the writer.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import _path

import unittest
from StringIO import StringIO

from serial.core import IStreamBuffer


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class IStreamBufferTest(unittest.TestCase):
    """ Unit testing for the IStreamBuffer class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.bufsize = 2
        self.buffer = IStreamBuffer(StringIO("abc\ndef\nghi\n"), self.bufsize)
        self.lines = ("abc\n", "def\n", "ghi\n")
        return

    def test_iter(self):
        """ Test the iterator protocol.

        Tests both __iter__() and next().

        """
        self.assertSequenceEqual(self.lines, list(self.buffer))
        return
        
    def test_rewind(self):
        """ Test the rewind() method.
        
        """
        self.buffer.next()
        self.buffer.rewind()  # back to first line
        self.assertSequenceEqual(self.lines, list(self.buffer))
        self.buffer.rewind(100)  # try to advance past beginning of buffer
        self.assertSequenceEqual(self.lines[-self.bufsize:], list(self.buffer))
        self.assertSequenceEqual([], list(self.buffer))  # stream is exhausted
        return


# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (IStreamBufferTest,)

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
