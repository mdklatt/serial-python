""" Testing for the the reader.py module

The script can be executed on its own or incorporated into a larger test suite.
However the tests are run, be aware of which version of the module is actually
being tested. If the library is installed in site-packages, that version takes
precedence over the version in this project directory. Use a virtualenv test
environment or setuptools develop mode to test against the development version.

"""
from io import StringIO
from collections import namedtuple

import pytest

from serial.core import IntField
from serial.core import ListField
from serial.core import StringField
from serial.core.reader import *  # tests __all__


@pytest.fixture
def records():
    return [
        {"int": 123, "arr": [{"x": "abc", "y": "def"}]},
        {"int": 456, "arr": [{"x": "ghi", "y": "jkl"}]},
        {"int": 789, "arr": [{"x": "mno", "y": "pqr"}]}]


def stop_filter(record):
    """ A filter function to stop iteration.

    """
    if record["int"] == 789:
        raise StopIteration
    return record


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


class _ReaderTest(object):
    """ Abstract base class for Reader unit testing.

    """
    def test_next(self, reader, records):
        """ Test the __next__() method.

        """
        assert next(reader) == records[0]

    def test_iter(self, reader, records):
        """ Test the __iter__() method.

        """
        assert list(reader) == records

    def test_filter(self, reader, records):
        """ Test the filter() method.

        """
        reader.filter(stop_filter, reject_filter, modify_filter)
        records[1]["int"] = 912
        assert list(reader) == records[1:2]
        return


class DictReaderTest(_ReaderTest):
    """ Unit testing for the DictReader class.

    """
    @classmethod
    @pytest.fixture
    def reader(cls, records):
        """ Return DictReader for testing.

        """
        return DictReader(records)

    def test_next_keys(self, records):
        """ Test the __next__() method for a subset of keys.

        """
        key = "int"
        records = [{key: record[key]} for record in records]
        reader = DictReader(records, [key])
        assert next(reader) == records[0]
        return


class ObjectReaderTest(_ReaderTest):
    """ Unit testing for the ObjectReader class.

    """
    @classmethod
    @pytest.fixture
    def reader(cls, records):
        """ Return an ObjectReader for testing.

        """
        attrs = list(records[0].keys())
        obj = namedtuple("Object", attrs)
        objects = [obj(**record) for record in records]
        return ObjectReader(objects, attrs)


class _TabularReaderTest(_ReaderTest):
    """ Abstract base class for tabular Reader unit testing.

    """
    TEST_CLASS = None  # must be defined by concrete classes

    @classmethod
    @pytest.fixture
    def reader(cls, stream, kwargs):
        """ Return a DelimitedReader for testing.

        """
        return cls.TEST_CLASS(stream, **kwargs)

    def test_open(self, stream, kwargs, records):
        """ Test the open method.

        """
        with self.TEST_CLASS.open(stream, **kwargs) as reader:
            assert next(reader) == records[0]
        assert stream.closed
        return


class DelimitedReaderTest(_TabularReaderTest):
    """ Unit testing for the DelimitedReader class.

    """
    TEST_CLASS = DelimitedReader

    @classmethod
    @pytest.fixture
    def kwargs(cls):
        """ Keyword arguments to initialize a reader.

        """
        fields = (
            IntField("int", 0),
            ListField("arr", (1, None), (
                StringField("x", 0),
                StringField("y", 1),)))
        return {"fields": fields, "delim": ",", "endl": "\n"}

    @classmethod
    @pytest.fixture
    def stream(cls):
        """ Return an input stream containing test data.

        """
        return StringIO("123, abc, def\n456, ghi, jkl\n789, mno, pqr\n")

    def test_iter_escape(self, kwargs, records):
        """ Test the __iter__() method with an escaped delimiter.

        """
        stream = StringIO("123, abc\\,, def\n456, ghi, jkl\n789, mno, pqr\n")
        kwargs["esc"] = "\\"
        reader = self.TEST_CLASS(stream, **kwargs)
        records[0]["arr"] = [{"x": "abc,", "y": "def"}]
        assert list(reader) == records
        return


class FixedWidthReaderTest(_TabularReaderTest):
    """ Unit testing for the FixedWidthReader class.

    """
    TEST_CLASS = FixedWidthReader

    @pytest.fixture
    def kwargs(self):
        """ Keyword arguments to initialize a reader.

        """
        fields = (
            IntField("int", (0, 4), "3d"),
            ListField("arr", (4, None), (
                StringField("x", (0, 4)),
                StringField("y", (4, 8)))))
        return {"fields": fields, "endl": "\n"}

    @pytest.fixture
    def stream(self):
        """ Return a test data stream.

        """
        return StringIO(" 123 abc def\n 456 ghi jkl\n 789 mno pqr\n")


class ChainReaderTest(object):
    """ Unit testing for the ChainReader class.

    """
    @classmethod
    @pytest.fixture
    def streams(cls):
        """ Return test data streams.

        """
        # Data for a FixedWidthReader
        data = " 123 abc def\n 456 ghi jkl\n", " 789 mno pqr\n"
        return map(StringIO, data)

    @classmethod
    def reader(cls, stream):
        """ Return a FixedWidthReader to read the test data.

        """
        fields = (
            IntField("int", (0, 4), "3d"),
            ListField("arr", (4, None), (
                StringField("x", (0, 4)),
                StringField("y", (4, 8)))))
        return FixedWidthReader(stream, fields)

    def test_next(self, streams, records):
        """ Test the __next__() method.

        """
        reader = ChainReader(streams, self.reader)
        assert next(reader) == records[0]

    def test_iter(self, streams, records):
        """ Test the __iter__() method.

        """
        reader = ChainReader(streams, self.reader)
        assert list(reader) == records
        assert all(stream.closed for stream in streams)
        return

    def test_iter_empty(self):
        """ Test the __iter__() method for an empty intput sequence.

        """
        reader = ChainReader([], self.reader)
        assert not list(reader)

    def test_open(self, streams, records):
        """

        """
        with ChainReader.open(streams, self.reader) as reader:
            assert next(reader) == records[0]
        assert all(stream.closed for stream in streams)


# Make the module executable.

if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
