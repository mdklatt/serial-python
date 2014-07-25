""" Testing for the the cache.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import _path
import _unittest as unittest

from serial.core.cache import *  # tests __all__


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class CacheReaderTest(unittest.TestCase):
    """ Unit testing for the CacheReader class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.records = {"str": "abc"}, {"str": "def"}, {"str": "ghi"}
        self.reader = CacheReader(iter(self.records))
        return

    def test_iter(self):
        """ Test the iterator protocol.

        Tests both __iter__() and next().

        """
        self.assertSequenceEqual(self.records, list(self.reader))
        return
        
    def test_rewind(self):
        """ Test the rewind() method.
        
        """
        list(self.reader)
        self.reader.rewind()
        self.reader.rewind()  # multiple rewinds should be a no-op
        self.assertSequenceEqual(self.records, list(self.reader))
        return

    def test_rewind_count(self):
        """ Test the rewind() method with a count argument.
        
        """
        count = 1
        list(self.reader)
        self.reader.rewind(count)
        self.assertSequenceEqual(self.records[-count:], list(self.reader))
        return

    def test_rewind_maxlen(self):
        """ Test the rewind() method with a maxlen value.
        
        """
        maxlen = 2
        self.reader = CacheReader(iter(self.records), maxlen)
        list(self.reader)
        self.reader.rewind(maxlen+1)  # attempt to rewind beyond buffer
        self.assertSequenceEqual(self.records[-maxlen:], list(self.reader))
        return
        

# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (CacheReaderTest,)

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
