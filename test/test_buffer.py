""" Testing for the the buffer.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import _path
import _unittest as unittest

from serial.core.buffer import _ReaderBuffer


class MockReaderBuffer(_ReaderBuffer):
    """ Concrete implementation of a _ReaderBuffer for testing.
    
    """
    def __init__(self, reader):
        """ Initialize this object.
        
        """
        super(MockReaderBuffer, self).__init__(reader)
        self._buffer = None
        return
        
    def _read(self, record):
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


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class MockReaderBufferTest(unittest.TestCase):
    """ Unit testing for the MockReaderBuffer class.

    Test a mock implemenation of _ReaderBuffer because the library doesn't
    define any concrete implementations.

    """    
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        reader = iter((
            # Need next() to simulate a reader.
            {"int": 123, "arr": [{"x": "abc", "y": "def"}]},
            {"int": 456, "arr": [{"x": "ghi", "y": "jkl"}]},
            {"int": 789, "arr": [{"x": "mno", "y": "pqr"}]}))        
        self.records = (
            {"int": 123, "arr": [{"x": "ghi", "y": "jkl"}]},
            {"int": 789, "arr": [{"x": "mno", "y": "pqr"}]})        
        self.buffer = MockReaderBuffer(reader)
        return

    def test_iter(self):
        """ Test the iterator protocol.

        Tests both __iter__() and next().

        """
        self.assertSequenceEqual(self.records, list(self.buffer))
        return


# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (MockReaderBufferTest,)

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
