""" Testing for the the sort.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
from operator import itemgetter
from random import shuffle
from unittest import TestCase
from unittest import TestSuite
from unittest import main

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

class _SortTest(TestCase):
    """ Base class for SortReaderTest and SortWriterTest.

    This is an abstract class and should not be called directly by any test
    runners.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.num_sorted = [{"num": x, "mod": x%2} for x in range(20)]
        self.mod_sorted = sorted(self.num_sorted, key=itemgetter("mod"))
        self.num_random = self.num_sorted[:]
        shuffle(self.num_random)
        self.mod_random = sorted(self.num_random, key=itemgetter("mod"))
        return


class SortReaderTest(_SortTest):
    """ Unit testing for the SortReader class.

    """
    def test_iter(self):
        """ Test the __iter__() method.
    
        """
        reader = SortReader(iter(self.num_random), "num")
        self.assertSequenceEqual(self.num_sorted, list(reader))
        return
        
    def test_iter_group(self):
        """ Test the __iter__() method with grouping.
    
        """
        reader = SortReader(iter(self.mod_random), "num", "mod")
        self.assertSequenceEqual(self.mod_sorted, list(reader))
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
        self.writer = _MockWriter()  
        return

    def test_write(self):
        """ Test the write() and close() methods.

        """
        writer = SortWriter(self.writer, "num")
        for record in self.num_random:
            writer.write(record)
        writer.close()
        writer.close()  # test that redundant calls are a no-op
        self.assertSequenceEqual(self.num_sorted, self.writer.output)
        return

    def test_write_group(self):
        """ Test the write() and dump() methods with grouping.

        """
        writer = SortWriter(self.writer, "num", "mod")
        writer.dump(self.mod_random)
        self.assertSequenceEqual(self.mod_sorted, self.writer.output)
        return


# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (SortReaderTest, SortWriterTest)

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
