""" Testing for the the reader.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import unittest
from io import BytesIO
from collections import namedtuple

from serial.core import ListField
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


class _ReaderTest(object):
    """ Abstract base class for Reader class unit testing.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.records = [
            {"int": 123, "arr": [{"x": "abc", "y": "def"}]},
            {"int": 456, "arr": [{"x": "ghi", "y": "jkl"}]}]
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


class DictReaderTest(_ReaderTest, unittest.TestCase):
    """ Read a sequence of dict-like items.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        super(DictReaderTest, self).setUp()
        self.reader = DictReader(self.records)
        return

    def test_next_keys(self):
        """ Test the next() method for a subset of keys.
        """
        key = "int"
        self.records = [{key: record[key]} for record in self.records]
        self.reader = DictReader(self.records, [key])
        self.test_next()
        return


class ObjectReaderTest(_ReaderTest, unittest.TestCase):
    """ Unit testing for the ObjectReader class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        super(ObjectReaderTest, self).setUp()
        attrs = self.records[0].keys()
        Object = namedtuple("Object", attrs)
        self.objects = [Object(**record) for record in self.records]
        self.reader = ObjectReader(self.objects, attrs)
        return


class _TabularReaderTest(_ReaderTest):
    """ Abstract base class for TabularReader class unit testing.

    """
    TestClass = None  # must be defined by derived classes

    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        super(_TabularReaderTest, self).setUp()
        self.stream = BytesIO(self.data)
        return

    def test_open(self):
        """ Test the open() method.

        """
        with self.TestClass.open(self.stream, **self.args) as self.reader:
            self.test_next()
        self.assertTrue(self.stream.closed)
        return


class DelimitedReaderTest(_TabularReaderTest, unittest.TestCase):
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
            ListField("arr", (1, None), (
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


class FixedWidthReaderTest(_TabularReaderTest, unittest.TestCase):
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
            ListField("arr", (4, None), (
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
        self.streams = BytesIO("abc\ndef\n"), BytesIO("ghi\njkl\n")
        self.records = "abc\n", "def\n", "ghi\n", "jkl\n"
        return

    def test_open(self):
        """ Test the open() method.

        """
        with ChainReader.open(self.streams, iter) as reader:
            self.assertSequenceEqual(self.records[0], reader.next())
        self.assertTrue(all(stream.closed for stream in self.streams))
        return

    def test_iter(self):
        """ Test the iterator protocol.

        """
        reader = ChainReader(self.streams, iter)
        self.assertSequenceEqual(self.records, list(reader))
        self.assertTrue(all(stream.closed for stream in self.streams))
        return

    def test_iter_empty(self):
        """ Test the iterator protocol for an empty input sequence.

        """
        reader = ChainReader((), iter)
        self.assertSequenceEqual((), list(reader))
        return


# Make the module executable.

if __name__ == "__main__":
    unittest.main()  # calls sys.exit()
