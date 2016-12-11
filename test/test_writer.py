""" Testing for the the writer.py module

The script can be executed on its own or incorporated into a larger test suite.
However the tests are run, be aware of which version of the module is actually
being tested. If the library is installed in site-packages, that version takes
precedence over the version in this project directory. Use a virtualenv test
environment or setuptools develop mode to test against the development version.

"""
from io import BytesIO

import pytest

from serial.core import IntField
from serial.core import ListField
from serial.core import StringField
from serial.core.writer import *  # tests __all__


@pytest.fixture
def records():
    return [
        {"int": 123, "arr": [{"x": "abc", "y": "def"}]},
        {"int": 456, "arr": [{"x": "ghi", "y": "jkl"}]}]


def reject_filter(record):
    """ A filter function to reject records.

    """
    return record if record["int"] != 789 else None


def modify_filter(record):
    """ A filter function to modify records.

    """
    record["int"] /= 2
    return record


class _WriterTest(object):
    """ Abstract base class for Writer unit testing.

    """
    # These values must be defined by child classes.
    TEST_CLASS = None
    OUTPUT = None

    @classmethod
    @pytest.fixture
    def stream(cls):
        return BytesIO()

    def test_write(self, stream, kwargs, records):
        """ Test the write() method.

        """
        writer = self.TEST_CLASS(stream, **kwargs)
        for record in records:
            writer.write(record)
        assert stream.getvalue() == self.OUTPUT
        return

    def test_open(self, stream, kwargs, records):
        """ Test the open() method.

        """
        with self.TEST_CLASS.open(stream, **kwargs) as writer:
            for record in records:
                writer.write(record)
            assert stream.getvalue() == self.OUTPUT
        assert stream.closed
        return

    def test_dump(self, stream, kwargs, records):
        """ Test the dump() method.

        """
        writer = self.TEST_CLASS(stream, **kwargs)
        writer.dump(records)
        assert stream.getvalue() == self.OUTPUT
        return

    def test_filter(self, stream, kwargs):
        """ Test the filter() method.

        """
        records = (
            {"int": 246, "arr": [{"x": "abc", "y": "def"}]},
            {"int": 912, "arr": [{"x": "ghi", "y": "jkl"}]},
            {"int": 789, "arr": [{"x": "mno", "y": "pqr"}]})
        writer = self.TEST_CLASS(stream, **kwargs)
        writer.filter(reject_filter, modify_filter)
        writer.dump(records)
        assert stream.getvalue() == self.OUTPUT
        return


class DelimitedWriterTest(_WriterTest):
    """ Unit testing for the DelimitedWriter class.

    """
    TEST_CLASS = DelimitedWriter
    OUTPUT = "123,abc,defX456,ghi,jklX"

    @classmethod
    @pytest.fixture
    def kwargs(cls):
        """ Keyword arguments to initialize a writer.

        """
        fields = (
            IntField("int", 0),
            ListField("arr", (1, None), (
                StringField("x", 0),
                StringField("y", 1),)))
        return {"fields": fields, "delim": ",", "endl": "X"}

    def test_write_escape(self, stream, kwargs, records):
        """ Test the write() method for escaped delimiters.

        """
        records[0]["arr"] = [{"x": "abc,", "y": "def"}]
        kwargs["esc"] = "\\"
        writer = self.TEST_CLASS(stream, **kwargs)
        writer.dump(records)
        assert stream.getvalue() == "123,abc\,,defX456,ghi,jklX"
        return


class FixedWidthWriterTest(_WriterTest):
    """ Unit testing for the FixedWidthWriter class.

    """
    TEST_CLASS = FixedWidthWriter
    OUTPUT = " 123abc def X 456ghi jkl X"

    @pytest.fixture
    def kwargs(self):
        """ Keyword arguments to initialize a writer.

        """
        fields = (
            IntField("int", (0, 4), "4d"),
            ListField("arr", (4, None), (
                StringField("x", (0, 4), "4s"),
                StringField("y", (4, 8), "4s"))))
        return {"fields": fields, "endl": "X"}


# Make the module executable.

if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
