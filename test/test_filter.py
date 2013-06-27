""" Testing for the the filter.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import _path
import _unittest as unittest

from serial.core import BlacklistFilter
from serial.core import WhitelistFilter


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class _FilterTest(unittest.TestCase):
    """ Unit testing for filter classes.

    This is an abstract class and should not be called directly by any test
    runners.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        Derived classes need to define the appropriate filter object.

        """
        self.accept = ({"test": "abc"}, {"test": "def"})
        self.reject = ({"test": "uvw"}, {"test": "xyz"})
        return
        
    def test_accept(self):
        """ Test for records that are accepted.

        """
        self.assertSequenceEqual(self.accept, map(self.filter, self.accept))
        return
        
    def test_reject(self):
        """ Test for records that are rejected.

        """
        self.assertSequenceEqual((None, None), map(self.filter, self.reject))
        return
        

class BlacklistFilterTest(_FilterTest):
    """ Unit testing for the BlacklistFilter class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        super(BlacklistFilterTest, self).setUp()
        self.filter = BlacklistFilter("test", ("uvw", "xyz"))
        return
        

class WhitelistFilterTest(_FilterTest):
    """ Unit testing for the WhitelistFilter class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        super(WhitelistFilterTest, self).setUp()
        self.filter = WhitelistFilter("test", ("abc", "def"))
        return


# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (BlacklistFilterTest, WhitelistFilterTest)

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
