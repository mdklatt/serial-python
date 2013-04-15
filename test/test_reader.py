""" Testing for the the dtype.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import _path

import StringIO
import unittest

from datalect.core import DelimitedReader
from datalect.core import FixedWidthReader
from datalect.core import IntType


# Utility functions.

def accept_filter(record):
    """ A filter function to accept records.
    
    """
    return True


def reject_filter(record):
    """ A filter function to reject records.
    
    """
    return record["A"] != 1  # reject if record["A"] == 1


def modify_filter(record):
    """ A filter function to modify records in place.
    
    """
    record["A"] *= 2  # modify in place
    return True


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class TabularReaderTest(unittest.TestCase):
    """ Unit testing for TabularReader classes.
    
    This is an abstract class and should not be called directly by any test
    runners.
    
    """
    def setUp(self):
        """ Set up the test fixture.
    
        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.
    
        """
        self.data = [{"A": 1, "B": 2}, {"A": 3, "B": 4}]
        return

    def test_next(self):
        """ Test the next() method.

        """
        self.assertEqual(self.data[0], self.reader.next())
        return

    def test_iter(self):
        """ Test the __iter__() method.

        """
        self.assertSequenceEqual(self.data, list(self.reader))
        return

    def test_filter_accept(self):
        """ Test a filter that accepts all records.
        
        """
        self.reader.filter(accept_filter)
        self.assertEqual(self.data[0], self.reader.next())
        return

    def test_filter_reject(self):
        """ Test a filter that rejects a record.
        
        """
        self.reader.filter(accept_filter)  # test chained filters
        self.reader.filter(reject_filter)
        self.assertEqual(self.data[1], self.reader.next())
        return

    def test_filter_modify(self):
        """ Test a filter that modifies records.
        
        """
        self.reader.filter(modify_filter)
        self.assertEqual({"A": 2, "B": 2}, self.reader.next())
        return


class DelimitedReaderTest(TabularReaderTest):
    """ Unit testing for the DelimitedReader class.
    
    """
    def setUp(self):
        """ Set up the test fixture.
    
        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.
    
        """
        super(DelimitedReaderTest, self).setUp()
        stream = StringIO.StringIO("1,2\n3,4\n")  
        fields = (("A", 0, IntType()), ("B", 1, IntType()))
        self.reader = DelimitedReader(stream, fields, ",")
        return
    

class FixedWidthReaderTest(TabularReaderTest):
    """ Unit testing for the FixedWidthReader class.
    
    """
    def setUp(self):
        """ Set up the test fixture.
    
        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.
    
        """
        super(FixedWidthReaderTest, self).setUp()
        stream = StringIO.StringIO(" 1 2\n 3 4\n")  
        fields = (("A", (0, 2), IntType()), ("B", (2, 4), IntType()))
        self.reader = FixedWidthReader(stream, fields)
        return
    

# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (DelimitedReaderTest, FixedWidthReaderTest)

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
