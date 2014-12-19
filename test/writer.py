""" Testing for the the writer.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
from io import BytesIO
from unittest import TestCase
from unittest import TestSuite
from unittest import main

from serial.core import DelimitedWriter
from serial.core import FixedWidthWriter
from serial.core import ListField
from serial.core import IntField
from serial.core import StringField


# Utility functions.

def reject_filter(record):
    """ A filter function to reject records.

    """
    return record if record["int"] != 123 else None


def modify_filter(record):
    """ A filter function to modify records.

    """
    record["int"] *= 2
    return record


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class _TabularWriterTest(TestCase):
    """ Unit testing for tabular writer classes.

    This is an abstract class and should not be called directly by any test
    runners.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.records = (
            {"int": 123, "arr": [{"x": "abc", "y": "def"}]},
            {"int": 456, "arr": [{"x": "ghi", "y": "jkl"}]})
        self.stream = BytesIO()
        return

    def test_open(self):
        """ Test the open() method.
        
        """
        with self.TestClass.open(self.stream, **self.args) as writer:
            self.test_write()
        self.assertTrue(self.stream.closed)
        return
        
    def test_write(self):
        """ Test the write() method.

        """
        for record in self.records:
            self.writer.write(record)
        self.assertEqual(self.data, self.stream.getvalue())
        return

    def test_dump(self):
        """ Test the dump() method.

        """
        self.writer.dump(self.records)
        self.assertEqual(self.data, self.stream.getvalue())
        return


class DelimitedWriterTest(_TabularWriterTest):
    """ Unit testing for the DelimitedWriter class.

    """
    TestClass = DelimitedWriter
    
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        fields = (
            IntField("int", 0),
            ListField("arr", (1, None), ( 
                StringField("x", 0), 
                StringField("y", 1))))
        super(DelimitedWriterTest, self).setUp()
        self.data = "123,abc,defX456,ghi,jklX"
        self.args = {"fields": fields, "delim": ",", "endl": "X"}
        self.writer = self.TestClass(self.stream, **self.args)
        return

    def test_write_escape(self):
        """ Test the write() method for escaped delimiters.
        
        """
        self.records[0]["arr"] = [{"x": "abc,", "y": "def"}]
        self.args["esc"] = "\\"
        self.writer = self.TestClass(self.stream, **self.args)
        self.data = "123,abc\,,defX456,ghi,jklX"
        self.test_write()
        return
    
    def test_filter(self):
        """ Test the filter() method.

        """
        self.writer.filter(reject_filter, modify_filter)
        self.data = "912,ghi,jklX"
        self.test_dump()
        return


class FixedWidthWriterTest(_TabularWriterTest):
    """ Unit testing for the DelimitedWriter class.

    """
    TestClass = FixedWidthWriter
    
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        fields = (
            IntField("int", (0, 4), "4d"),
            ListField("arr", (4, None), (
                StringField("x", (0, 4), "4s"), 
                StringField("y", (4, 8), "4s")))) 
        super(FixedWidthWriterTest, self).setUp()
        self.data = " 123abc def X 456ghi jkl X"
        self.args = {"fields": fields, "endl": "X"}
        self.writer = self.TestClass(self.stream, **self.args)
        return

    def test_filter(self):
        """ Test a filter that modifies records

        """
        self.writer.filter(reject_filter, modify_filter)
        self.data = " 912ghi jkl X"
        self.test_dump()
        return


# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (DelimitedWriterTest, FixedWidthWriterTest)

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