""" Testing for the the aggregate.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import _path
import _unittest as unittest

from io import BytesIO

from serial.core import IntField
from serial.core import FloatField
from serial.core import StringField

from serial.core.aggregate import *  # tests __all__


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class AggregateReaderTest(unittest.TestCase):
    """ Unit testing for tabular reader classes.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.records = (
            {"str": "abc", "int": 1, "float": 1.},
            {"str": "abc", "int": 1, "float": 2.},
            {"str": "abc", "int": 3, "float": 3.},
            {"str": "def", "int": 3, "float": 4.})
        return

    def test_iter(self):
        """ Test the iterator protocol.

        """
        aggregate = (
            {"str": "abc", "int": 5, "float": 3.},
            {"str": "def", "int": 3, "float": 4.})
        reader = AggregateReader(iter(self.records), "str")
        reader.apply("int", sum)
        reader.apply("float", max)        
        self.assertSequenceEqual(aggregate, list(reader))
        return
        
    def test_iter_multi(self):
        """ Test the iterator protocol with multi-key grouping.
        
        """
        aggregate = (
            {"str": "abc", "int": 1, "float": 3.},
            {"str": "abc", "int": 3, "float": 3.},
            {"str": "def", "int": 3, "float": 4.})
        reader = AggregateReader(iter(self.records), ("str", "int"))        
        reader.apply("float", sum)        
        self.assertSequenceEqual(aggregate, list(reader))
        return
        


# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (AggregateReaderTest,)

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
