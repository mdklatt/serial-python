""" Testing for the the buffer.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import _path
import _unittest as unittest

from serial.core.buffer import _ReaderBuffer
from serial.core.buffer import _WriterBuffer


# The library doesn't include any concrete implementations of _ReaderBuffer or
# _WriterBuffer, so create sample implementations

class ReaderBuffer(_ReaderBuffer):
    """ Concrete implementation of a _ReaderBuffer for testing.
    
    """
    def __init__(self, reader):
        """ Initialize this object.
        
        """
        super(ReaderBuffer, self).__init__(reader)
        self._buffer = None
        return
        
    def _queue(self, record):
        """ Merge every two records.
        
        """
        if not self._buffer:
            # First record in a pair.
            self._buffer = record
        else:
            # Complete the pair.
            record["int"] = self._buffer["int"]
            self._output.append(record)
            self._buffer = None
        return

    def _flush(self):
        """ Complete any buffering operations. 
        
        """
        if self._buffer:
            # No more input, so output the last record as-is.
            self._output.append(self._buffer)
        return


class WriterBuffer(_WriterBuffer):
    """ Concrete implementation of a _WriterBuffer for testing.
    
    """
    def __init__(self, writer):
        """ Initialize this object.
        
        """
        super(WriterBuffer, self).__init__(writer)
        self._buffer = None
        return
        
    def _queue(self, record):
        """ Merge every two records.
        
        """
        if not self._buffer:
            # First record in a pair.
            self._buffer = record
        else:
            # Complete the pair.
            record["int"] = self._buffer["int"]
            self._output.append(record)
            self._buffer = None
        return

    def _flush(self):
        """ Complete any buffering operations. 
        
        """
        if self._buffer:
            # No more input, so output the last record as-is.
            self._output.append(self._buffer)
        return


# Mock objects to use for testing.

class MockReader(object):
    """ Simulate a _Reader for testing purposes.
    
    """
    def __init__(self, records):
        """ Initialize this object.
        
        """
        self._iter = iter(records)
        self.next = self._iter.next
        return
                
        
class MockWriter(object):
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

class _BufferTest(unittest.TestCase):
    """ Unit testing for buffer classes.

    This is an abstract class and should not be called directly by any test
    runners.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        Derived classes need to define the appropriate filter object.

        """
        self.input = (
            {"int": 123, "arr": [{"x": "abc", "y": "def"}]},
            {"int": 456, "arr": [{"x": "ghi", "y": "jkl"}]},
            {"int": 789, "arr": [{"x": "mno", "y": "pqr"}]})
        self.output = (
            {"int": 123, "arr": [{"x": "ghi", "y": "jkl"}]},
            {"int": 789, "arr": [{"x": "mno", "y": "pqr"}]})
        self.reader = MockReader(self.input)
        self.writer = MockWriter()   
        return


class ReaderBufferTest(_BufferTest):
    """ Unit testing for the ReaderBuffer class.

    """    
    def test_iter(self):
        """ Test the iterator protocol.

        Tests both __iter__() and next().

        """
        buffer = ReaderBuffer(self.reader)
        self.assertSequenceEqual(self.output, list(buffer))
        return


class WriterBufferTest(_BufferTest):
    """ Unit testing for the WriterBuffer class.

    """    
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        Derived classes need to define the appropriate filter object.

        """
        super(WriterBufferTest, self).setUp()
        self.buffer = WriterBuffer(self.writer)  
        return

    def test_write(self):
        """ Test the write() method.

        """
        for record in self.input:
            self.buffer.write(record)
        self.buffer.close()
        self.assertSequenceEqual(self.output, self.writer.output)
        return

    def test_dump(self):
        """ Test the dump() method.

        """
        self.buffer.dump(self.input)
        self.assertSequenceEqual(self.output, self.writer.output)
        return


# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (ReaderBufferTest, WriterBufferTest)

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
