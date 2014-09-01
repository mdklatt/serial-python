""" Testing for the the filter.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import _unittest as unittest

from serial.core.filter import *  # tests __all__


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class _FilterTest(unittest.TestCase):
    """ Unit testing for filter classes.

    This is an abstract class and should not be called directly by any test
    runners.

    """
    def test_whitelist(self):
        """ Test the __call__ method for whitelisting.
        
        """ 
        filtered = self.data[:2] + [None]
        self.assertSequenceEqual(filtered, map(self.whitelist, self.data))
        return
    
    def test_blacklist(self):
        """ Test the __call__ method for blacklisting.
        
        """ 
        filtered = [None]*2 + self.data[2:]
        self.assertSequenceEqual(filtered, map(self.blacklist, self.data))
        return


class _RecordFilterTest(_FilterTest):
    """
    """
    def test_whitelist_missing(self):
        """ Test the __call__ method with a missing field.
        
        """ 
        self.data = [{"not_test": value} for value in self.values]
        filtered = [None] * len(self.data)
        self.assertSequenceEqual(filtered, map(self.whitelist, self.data))
        return
    
    def test_blacklist_missing(self):
        """ Test the __call__ method for blacklisting with a missing field.
        
        """
        self.data = [{"not_test": value} for value in self.values]
        self.assertSequenceEqual(self.data, map(self.blacklist, self.data))
        return
    
    
class FieldFilterTest(_RecordFilterTest):
    """ Unit testing for the FieldFilter class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        # Filters need to match the first two records.
        self.values = ("abc", "def", "ghi")
        self.whitelist = FieldFilter("test", self.values[:2])
        self.blacklist = FieldFilter("test", self.values[:2], True)
        self.data = [{"test": value} for value in self.values]
        return

               
class RangeFilterTest(_RecordFilterTest):
    """ Unit testing for the RangeFilter class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        # Filters need to match the first two records.
        self.values = (1, 2, 3)
        self.whitelist = RangeFilter("test", 1, 3)
        self.blacklist = RangeFilter("test", 1, 3, True)
        self.data = [{"test": value} for value in self.values]
        return

    def test_no_start(self):
        """ Test the __call__ method with no lower limit.
        
        """
        self.whitelist = RangeFilter("test", stop=3)
        filtered = self.data[:2] + [None]
        self.assertSequenceEqual(filtered, map(self.whitelist, self.data))
        return

    def test_no_stop(self):
        """ Test the __call__ method with no upper limit.
        
        """
        self.whitelist = RangeFilter("test", 2)
        filtered = [None] + self.data[1:]
        self.assertSequenceEqual(filtered, map(self.whitelist, self.data))
        return


class RegexFilterTest(_FilterTest):
    """ Unit testing for the RegexFilter class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        # Filters need to match the first two lines.
        regex = r"abc|def"
        self.whitelist = RegexFilter(regex)
        self.blacklist = RegexFilter(regex, True)
        self.data = ["abc\n", "def\n", "ghi\n"]
        return


class SliceFilterTest(_FilterTest):
    """ Unit testing for the SliceFilter class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        # Filters need to match the first two lines. This will test both types
        # of slice expressions.
        values = ("bc", "ef")
        self.whitelist = SliceFilter((1, 3), values)
        self.blacklist = SliceFilter(slice(1, 3), values, True)
        self.data = ["abc\n", "def\n", "ghi\n"]
        return

        
# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (FieldFilterTest, RangeFilterTest, RegexFilterTest, 
               SliceFilterTest)

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
    unittest.main()  # this calls exit()
