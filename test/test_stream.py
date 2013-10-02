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

import _path
import _unittest as unittest

from serial.core import IStreamBuffer
from serial.core import IStreamFilter
from serial.core import IStreamZlib
from serial.core import IFileSequence


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
        for _ in range(2):
            self.stream.next()
        self.stream.rewind(2)
        self.assertSequenceEqual(self.lines, list(self.stream))
        self.stream.rewind()  # back to beginning of buffer
        self.assertSequenceEqual(self.lines[-self.bufsize:], list(self.stream))
        self.assertSequenceEqual([], list(self.stream))  # stream is exhausted
        return


class IStreamFilterTest(unittest.TestCase):
    """ Unit testing for the IStreamFilter class.
    
    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.lines = ("abc\n", "def\n", "ghi\n")
        self.stream = StringIO("".join(self.lines))
        return
    
    def test_filter(self):
        """ Test filtering.
        
        """
        reject_filter = lambda line: line if line[0] != "d" else None
        modify_filter = lambda line: line.upper()
        stream = IStreamFilter(self.stream, reject_filter, modify_filter)
        self.assertSequenceEqual(("ABC\n", "GHI\n"), list(stream))
        return

    def test_filter_stop(self):
        """ Test a filter that stops iteration.
        
        """
        def stop_filter(line):
            """ Filter that stops iteration. """
            if line[0] == "d":
                raise StopIteration
            return line
            
        stream = IStreamFilter(self.stream, stop_filter)
        self.assertSequenceEqual(("abc\n",), list(stream))
        return
    
    
class IStreamZlibTest(unittest.TestCase):
    """ Unit testing for the IStreamZlib class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        # Test blank lines, lines that are longer and shorter than the block
        # size, and no trailing \n.
        IStreamZlib.block_size = 4
        self.lines = ("\n", "abcdefgh\n", "ijkl")
        return

    def test_iter_gzip(self):
        """ Test the iterator protocol for gzip data.
        
        """    
        buffer = BytesIO()
        with  closing(GzipFile(fileobj=buffer, mode="w")) as stream:
            # Explicit closing() context is necessary for Python 2.6 but not
            # for 2.7.
            stream.write("".join(self.lines))
        buffer.seek(0)
        self.assertSequenceEqual(self.lines, list(IStreamZlib(buffer)))
        return

    def test_iter_zlib(self):
        """ Test the iterator protocol for zlib data.
    
        """
        buffer = BytesIO(compress("".join(self.lines)))
        stream = IStreamZlib(buffer)
        self.assertSequenceEqual(self.lines, list(stream))
        return
    

class IFileSequenceTest(unittest.TestCase):
    """ Unit testing for the IFileSequence class.
    
    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.lines = ["abc\n", "def\n", "ghi\n"]
        self.paths = []
        for _ in range(2):
            stream = NamedTemporaryFile("w", delete=False)
            map(stream.write, self.lines)
            stream.close()
            self.paths.append(stream.name)
        return

    def test_iter(self):
        """ Test the iterator protocol.
        
        """
        stream = IFileSequence(*self.paths)
        self.assertSequenceEqual(self.lines * 2, list(stream))
        return

    def test_iter_error(self):
        """ Test the iterator protocol for a missing file.
        
        """
        self.paths.insert(1, "none")  # nonexistent file
        stream = IFileSequence(*self.paths)
        self.assertRaises(IOError, list, stream)
        return

    def test_iter_glob(self):
        """ Test the iterator protocol with globbing.
        
        """
        # Test for wildcards and the supression of errors for nonexistent
        # files.
        for pos, path in enumerate(self.paths):
            self.paths[pos] = path + "*"
        self.paths.insert(1, "none")  # nonexistent file
        stream = IFileSequence(*self.paths, glob=True)
        self.assertSequenceEqual(self.lines * 2, list(stream))
        return
        
    def tearDown(self):
        """ Tear down the test fixture.

        This is called after each test is run. This is part of the unittest 
        API.

        """
        # Remove temporary files.
        for path in self.paths:
            try:
                remove(path)
            except OSError:
                pass
        return


# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (IStreamBufferTest, IStreamFilterTest, IStreamZlibTest, 
               IFileSequenceTest)

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
