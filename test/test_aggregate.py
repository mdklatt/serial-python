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


class _AggregateTest(unittest.TestCase):
    """ Unit testing for tabular reader classes.

    This is an abstract class and should not be called directly by any test
    runners.

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
    

class AggregateReaderTest(_AggregateTest):
    """ Unit testing for tabular reader classes.

    """
    def test_iter(self):
        """ Test the iterator protocol.

        """
        aggregate = (
            {"str": "abc", "int": 5, "float": 3.},
            {"str": "def", "int": 3, "float": 4.})
        reader = AggregateReader(iter(self.records), "str")
        reader.reduce("int", sum)
        reader.reduce("float", max)        
        self.assertSequenceEqual(aggregate, list(reader))
        return
        
    def test_iter_multi(self):
        """ Test the iterator protocol with multi-key grouping.
        
        """
        aggregate = (
            {"str": "abc", "int": 1, "float": 2.},
            {"str": "abc", "int": 3, "float": 3.},
            {"str": "def", "int": 3, "float": 4.})
        reader = AggregateReader(iter(self.records), ("str", "int"))        
        reader.reduce("float", max)        
        self.assertSequenceEqual(aggregate, list(reader))
        return


class AggregateWriterTest(_AggregateTest):
    """ Unit testing for tabular writer classes.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        super(AggregateWriterTest, self).setUp()
        self.buffer = _MockWriter()  
        return

    def test_write(self):
        """ Test the write() and close() methods.

        """
        aggregate = (
            {"str": "abc", "int": 5, "float": 3.},
            {"str": "def", "int": 3, "float": 4.})
        writer = AggregateWriter(self.buffer, "str")
        writer.reduce("int", sum)
        writer.reduce("float", max)        
        for record in self.records:
            writer.write(record)
        writer.close()
        writer.close()  # test that redundant calls are a no-op
        self.assertSequenceEqual(aggregate, self.buffer.output)
        return

    def test_write_multi_key(self):
        """ Test the write() and close() methods with multi-key grouping.

        """
        aggregate = (
            {"str": "abc", "int": 1, "float": 2.},
            {"str": "abc", "int": 3, "float": 3.},
            {"str": "def", "int": 3, "float": 4.})
        writer = AggregateWriter(self.buffer, ("str", "int"))
        writer.reduce("float", max)        
        for record in self.records:
            writer.write(record)
        writer.close()
        writer.close()  # test that redundant calls are a no-op
        self.assertSequenceEqual(aggregate, self.buffer.output)
        return


# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (AggregateReaderTest, AggregateWriterTest)

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
