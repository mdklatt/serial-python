""" Testing for the the reader.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import _path
import _unittest as unittest

from functools import partial
from io import BytesIO

from serial.core import ArrayField
from serial.core import IntField
from serial.core import StringField

from serial.core.reader import *  # tests __all__


# Utility functions and classes.

def reject_filter(record):
    """ A filter function to reject records.

    """
    return record if record["int"] != 123 else None


def modify_filter(record):
    """ A filter function to modify records.

    """
    # Input filters can safely modify record.
    record["int"] *= 2 
    return record


def stop_filter(record):
    """ A filter function to stop iteration.

    """
    if record["int"] == 456:
        raise StopIteration
    return record


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class _TabularReaderTest(unittest.TestCase):
    """ Unit testing for tabular reader classes.

    This is an abstract class and should not be called directly by any test
    runners.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.records = [
            {"int": 123, "arr": [{"x": "abc", "y": "def"}]},
            {"int": 456, "arr": [{"x": "ghi", "y": "jkl"}]}]
        self.stream = BytesIO(self.data)
        return

    def test_open(self):
        """ Test the open() method.
        
        """
        with self.TestClass.open(self.stream, **self.args) as self.reader:
            self.test_next()
        self.assertTrue(self.stream.closed)
        return

    def test_next(self):
        """ Test the next() method.

        """
        
        # TODO: Test with nonstandard line endings.
        self.assertEqual(self.records[0], self.reader.next())
        return

    def test_iter(self):
        """ Test the __iter__() method.

        """
        self.assertSequenceEqual(self.records, list(self.reader))
        return

    def test_filter(self):
        """ Test the filter method().

        """
        self.records = self.records[1:]
        self.records[0]["int"] = 912
        self.reader.filter(reject_filter, modify_filter)
        self.test_iter()
        return

    def test_filter_stop(self):
        """ Test a filter that stops iteration.

        """
        self.records = self.records[:1]
        self.reader.filter(stop_filter)
        self.test_iter()
        return


class DelimitedReaderTest(_TabularReaderTest):
    """ Unit testing for the DelimitedReader class.

    """
    TestClass = DelimitedReader
    
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        fields = (
            IntField("int", 0, ),
            ArrayField("arr", (1, None), (
                StringField("x", 0), 
                StringField("y", 1))))
        self.data = "123, abc, def\n456, ghi, jkl\n"
        super(DelimitedReaderTest, self).setUp()
        self.args = {"fields": fields, "delim": ",", "endl": "\n"}
        self.reader = self.TestClass(self.stream, **self.args)
        return
        
    def test_iter_escape(self):
        """ Test the __iter__() method with an escaped delimiter.
    
        """
        self.stream = BytesIO("123, abc\,, def\n456, ghi, jkl\n")
        self.args["esc"] = "\\"
        self.reader = self.TestClass(self.stream, **self.args)
        self.records[0]["arr"] = [{"x": "abc,", "y": "def"}]
        self.test_iter()
        return
        

class FixedWidthReaderTest(_TabularReaderTest):
    """ Unit testing for the FixedWidthReader class.

    """
    TestClass = FixedWidthReader
    
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        fields = (
            IntField("int", (0, 4), "3d"),
            ArrayField("arr", (4, None), ( 
                StringField("x", (0, 4)), 
                StringField("y", (4, 8)))))
        self.data = " 123 abc def\n 456 ghi jkl\n"
        super(FixedWidthReaderTest, self).setUp()
        self.args = {"fields": fields, "endl": "\n"}
        self.reader = self.TestClass(self.stream, **self.args)
        return


class ChainReaderTest(unittest.TestCase):
    """ Unit testing for the ChainReader class.
    
    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.delim = ","
        self.fields = (IntField("int", (0, 4)), StringField("str", (4, 8)))
        data = " 123 abc\n 456 def\n"
        self.streams = (BytesIO(data), BytesIO(data.upper()))
        self.records = (
            {"int": 123, "str": "abc"}, {"int": 456, "str": "def"},
            {"int": 123, "str": "ABC"}, {"int": 456, "str": "DEF"})
        return

    def test_open(self):
        """ Test the open() method.
        
        """
        with ChainReader.open(self.streams, FixedWidthReader, 
                                 self.fields) as reader: 
            self.assertSequenceEqual(self.records[0], reader.next())
        self.assertTrue(all(stream.closed for stream in self.streams))
        return
    
    def test_iter(self):
        """ Test the iterator protocol.
        
        """
        reader = ChainReader(self.streams, FixedWidthReader, self.fields) 
        self.assertSequenceEqual(self.records, list(reader))
        self.assertTrue(all(stream.closed for stream in self.streams))
        return
    
    def test_iter_empty(self):
        """ Test the iterator protocol for an empty input sequence.
        
        """
        reader = ChainReader((), FixedWidthReader, self.fields)
        self.assertSequenceEqual((), list(reader))
        return
        

class ReaderSequenceTest(unittest.TestCase):
    
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        fields = (
            IntField("int", 0, ),
            ArrayField("arr", (1, None), (
                StringField("x", 0), 
                StringField("y", 1))))
        self.reader = partial(DelimitedReader, fields=fields, delim=",")
        data = "123, abc, def\n456, ghi, jkl\n"
        self.streams = (BytesIO(data), BytesIO(data.upper()))
        self.records = (
            {"int": 123, "arr": [{"x": "abc", "y": "def"}]},
            {"int": 456, "arr": [{"x": "ghi", "y": "jkl"}]},
            {"int": 123, "arr": [{"x": "ABC", "y": "DEF"}]},
            {"int": 456, "arr": [{"x": "GHI", "y": "JKL"}]})
        return

    def test_iter(self):
        """ Test the __iter__() method.
        
        """
        sequence = ReaderSequence(self.reader, *self.streams)
        self.assertSequenceEqual(self.records, list(sequence))
        self.assertTrue(all(stream.closed for stream in self.streams))
        return
        
    def test_iter_context(self):
        """ Test the __iter__() method inside a context block.
        
        """
        with ReaderSequence(self.reader, *self.streams) as sequence:
            self.assertSequenceEqual(self.records, list(sequence))
        self.assertTrue(all(stream.closed for stream in self.streams))
        return
        
    def test_iter_empty(self):
        """ Test the __iter__() method for an empty input sequence.
        
        """
        with ReaderSequence(self.reader) as sequence:
            self.assertSequenceEqual((), list(sequence))
        return


# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (DelimitedReaderTest, FixedWidthReaderTest, ChainReaderTest,
               ReaderSequenceTest)

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
