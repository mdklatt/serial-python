""" Testing for the the filter.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import _path
import _unittest as unittest

from serial.core import FieldFilter
from serial.core import TextFilter

# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.


class _FilterTest(unittest.TestCase):
    """ Unit testing for filter classes.

    This is an abstract class and should not be called directly by any test
    runners.

    """
    def test_call(self):
        """ Test the __call__ method.
        
        """ 
        filtered = self.data[:2] + [None]
        self.assertSequenceEqual(filtered, map(self.whitelist, self.data))
        return
    
    def test_call_blacklist(self):
        """ Test the __call__ method for blacklisting.
        
        """ 
        filtered = [None]*2 + self.data[2:]
        self.assertSequenceEqual(filtered, map(self.blacklist, self.data))
        return


class FieldFilterTest(_FilterTest):
    """ Unit testing for the FieldFilter class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        # Filters need to match the first two records.
        values = ("abc", "def", "ghi")
        self.whitelist = FieldFilter("test", values[:2])
        self.blacklist = FieldFilter("test", values[:2], False)
        self.data = [{"test": value} for value in values]
        return

                
class TextFilterTest(_FilterTest):
    """ Unit testing for the WhitelistFilter class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        # Filters need to match the first two lines.
        regex = r"abc|def"
        self.whitelist = TextFilter(regex)
        self.blacklist = TextFilter(regex, False)
        self.data = ["abc\n", "def\n", "ghi\n"]
        return

        
# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (FieldFilterTest, TextFilterTest)

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
    unittest.main()  # this calls sys.exit()
