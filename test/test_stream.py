""" Testing for the the writer.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
from StringIO import StringIO
from io import BytesIO
from zlib import compress

import _path
import _unittest as unittest

from serial.core import IStreamBuffer
from serial.core import IStreamZlib


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
        self.lines = ("abc\n", "def\n", "ghi\n")
        stream = StringIO("".join(self.lines))
        self.stream = IStreamBuffer(stream, self.bufsize)
        return

    def test_iter(self):
        """ Test the iterator protocol.

        Tests both __iter__() and next().

        """
        self.assertSequenceEqual(self.lines, list(self.stream))
        return
        
    def test_rewind(self):
        """ Test the rewind() method.
        
        """
        self.stream.next()
        self.stream.rewind()  # back to first line
        self.assertSequenceEqual(self.lines, list(self.stream))
        self.stream.rewind(100)  # try to advance past beginning of buffer
        self.assertSequenceEqual(self.lines[-self.bufsize:], list(self.stream))
        self.assertSequenceEqual([], list(self.stream))  # stream is exhausted
        return

class IStreamZlibTest(unittest.TestCase):
    """ Unit testing for the IStreamZlib class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.lines = ("abcd\n", "efgh\n", "ijkl")  # test with missing newline
        self.stream = IStreamZlib(BytesIO(compress("".join(self.lines))))
        return

    def test_iter_zlib(self):
        """ Test the iterator protocol.
    
        Tests both __iter__() and next().
    
        """
        self.assertSequenceEqual(self.lines, list(self.stream))
        return

    def test_iter_long(self):
        """ Test the iterator protocol for long lines.

        Tests both __iter__() and next().

        """
        # Test for lines longer than than the block size.
        self.stream.block_size = 4  # minimum block size
        self.assertSequenceEqual(self.lines, list(self.stream))
        return

# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (IStreamBufferTest, IStreamZlibTest)

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
