""" Testing for the the filter.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import _path
import _unittest as unittest

from serial.core import FieldFilter

# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class FieldFilterTest(unittest.TestCase):
    """ Unit testing for the WhitelistFilter class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.records = ({"field": "abc"}, {"field": "def"}, {"field": "ghi"})
        return
        
    def test_call(self):
        """ Test the __call__ method.
        
        """
        whitelist = FieldFilter("field", ("abc", "def"))
        filtered = (self.records[0], self.records[1], None)
        self.assertSequenceEqual(filtered, map(whitelist, self.records))
        return
        
    def test_call_blacklist(self):
        """ Test the __call__ method with blacklisting.
        
        """
        blacklist = FieldFilter("field", ("abc", "def"), False)
        filtered = (None, None, self.records[2])
        self.assertSequenceEqual(filtered, map(blacklist, self.records))
        return
        

# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (FieldFilterTest,)

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
