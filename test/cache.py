""" Testing for the the cache.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
from unittest import TestCase
from unittest import TestSuite
from unittest import main

from serial.core.cache import *  # tests __all__


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class CacheReaderTest(TestCase):
    """ Unit testing for the CacheReader class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        # Need at least 3 records.
        self.records = {"str": "abc"}, {"str": "def"}, {"str": "ghi"}
        self.reader = CacheReader(iter(self.records))
        return

    def test_iter(self):
        """ Test the iterator protocol.

        Tests both __iter__() and next().

        """
        self.assertSequenceEqual(self.records, list(self.reader))
        return

    def test_iter_empty(self):
        """ Test the iterator protocol with empty input.
        
        """
        self.reader = CacheReader(iter([]))
        self.assertSequenceEqual([], list(self.reader))
        return
                
    def test_rewind(self):
        """ Test the rewind() method.
        
        """
        list(self.reader)  # exhaust reader
        self.reader.rewind()
        self.reader.rewind()  # should be a no-op
        self.assertSequenceEqual(self.records, list(self.reader))
        return

    def test_rewind_count(self):
        """ Test the rewind() method with a count argument.
        
        """
        count = 1
        list(self.reader)  # exhaust reader
        self.reader.rewind(count)
        self.assertSequenceEqual(self.records[-count:], list(self.reader))
        return

    def test_rewind_maxlen(self):
        """ Test the rewind() method with a maxlen value.
        
        """
        maxlen = len(self.records) - 1
        self.reader = CacheReader(iter(self.records), maxlen)
        list(self.reader)  # exhaust reader
        self.reader.rewind(maxlen+1)  # attempt to rewind beyond cache
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
    suite = TestSuite()
    for test_case in _TEST_CASES:
        tests = loader.loadTestsFromTestCase(test_case)
        suite.addTests(tests)
    return suite


# Make the module executable.

if __name__ == "__main__":
    main()  # main() calls sys.exit()