""" Testing for the the stream.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
from contextlib import closing
from gzip import GzipFile
from io import BytesIO
from StringIO import StringIO
from os import remove
from tempfile import NamedTemporaryFile

from zlib import compress
from zlib import decompress

import _path
import _unittest as unittest

from serial.core import BufferedIStream
from serial.core import FilteredIStream
from serial.core import FilteredOStream
from serial.core import GzippedIStream


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class BufferedIStreamTest(unittest.TestCase):
    """ Unit testing for the BufferedIStream class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.bufsize = 2
        self.lines = ("abc\n", "def\n", "ghi\n")
        stream = StringIO("".join(self.lines))
        self.stream = BufferedIStream(stream, self.bufsize)
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
        for _ in range(2):
            self.stream.next()
        self.stream.rewind(2)
        self.assertSequenceEqual(self.lines, list(self.stream))
        self.stream.rewind()  # back to beginning of buffer
        self.assertSequenceEqual(self.lines[-self.bufsize:], list(self.stream))
        self.assertSequenceEqual([], list(self.stream))  # stream is exhausted
        return


class FilteredIStreamTest(unittest.TestCase):
    """ Unit testing for the FilteredIStream class.
    
    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.lines = ("abc\n", "def\n", "ghi\n")
        self.stream = StringIO("".join(self.lines))
        return

    def test_iter(self):
        """ Test the iterator protocol.
        
        This tests both the __iter__() and next() methods.
        
        """
        reject_filter = lambda line: line if line[0] != "d" else None
        modify_filter = lambda line: line.upper()
        stream = FilteredIStream(self.stream, reject_filter, modify_filter)
        self.assertSequenceEqual(("ABC\n", "GHI\n"), list(stream))
        return

    def test_iter_stop(self):
        """ Test the iterator protocol with a filter that stops iteration
        
        """
        def stop_filter(line):
            """ Filter that stops iteration. """
            if line[0] == "d":
                raise StopIteration
            return line
            
        stream = FilteredIStream(self.stream, stop_filter)
        self.assertSequenceEqual(("abc\n",), list(stream))
        return
 

class FilteredOStreamTest(unittest.TestCase):
    """ Unit testing for the FilteredIStream class.
    
    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.lines = ("abc\n", "def\n", "ghi\n")
        self.data = "ABC\nGHI\n"
        self.stream = StringIO()
        return

    def test_write(self):
        """ Test the write() method.
        
        """
        reject_filter = lambda line: line if line[0] != "d" else None
        modify_filter = lambda line: line.upper()
        stream = FilteredOStream(self.stream, reject_filter, modify_filter)
        for line in self.lines:
            stream.write(line)
        self.assertEqual(self.data, self.stream.getvalue())
        return

 
class GzippedIStreamTest(unittest.TestCase):
    """ Unit testing for the GzippedIStream class.
    
    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        # Test blank lines, lines longer, shorter, and equal to the block size,
        # and no trailing \n.
        GzippedIStream.block_size = 4
        self.lines = ("\n", "abcdefgh\n", "ijkl")
        self.zlib_data = BytesIO(compress("".join(self.lines)))
        self.gzip_data = BytesIO()
        with  closing(GzipFile(fileobj=self.gzip_data, mode="w")) as stream:
            # Explicit closing() context is necessary for Python 2.6 but not
            # for 2.7. Closing stream doesn't close fileobj.
            stream.write("".join(self.lines))
        self.gzip_data.seek(0)  # rewind for reading
        return

    def test_iter_gzip(self):
        """ Test the iterator protocol for gzip data.
        
        """    
        self.assertSequenceEqual(self.lines, list(GzippedIStream(self.gzip_data)))
        return

    def test_iter_zlib(self):
        """ Test the iterator protocol for zlib data.
    
        """
        self.assertSequenceEqual(self.lines, list(GzippedIStream(self.zlib_data)))
        return


# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (BufferedIStreamTest, FilteredIStreamTest, FilteredOStreamTest,
               GzippedIStreamTest)

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
