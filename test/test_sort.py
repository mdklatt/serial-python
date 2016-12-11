""" Testing for the the sort.py module

The script can be executed on its own or incorporated into a larger test suite.
However the tests are run, be aware of which version of the module is actually
being tested. If the library is installed in site-packages, that version takes
precedence over the version in this project directory. Use a virtualenv test
environment or setuptools develop mode to test against the development version.

"""
import pytest
from operator import itemgetter
from random import shuffle

from _fixture import writer
from serial.core.sort import *  # tests __all__


@pytest.fixture
def records():
    """ Return randomly-ordered test records.

    """
    records = [{"num": x, "mod": x % 2} for x in range(10)]
    shuffle(records)
    return records


class SortReaderTest(object):
    """ Unit testing for the SortReader class.

    """
    def test_iter(self, records):
        """ Test the iterator protocol.

        """
        key = "num"
        reader = iter(records)
        sorter = SortReader(reader, "num")
        assert list(sorter) == sorted(records, key=itemgetter(key))
        return

    def test_iter_multi(self, records):
        """ Test the iterator protocol with a multi-value key.

        """
        key = "mod", "num"
        reader = iter(records)
        sorter = SortReader(reader, key)
        assert list(sorter) == sorted(records, key=itemgetter(*key))
        return

    def test_iter_custom(self, records):
        """ Test the iterator protocol with a custom key function.

        """
        key = itemgetter("num")
        reader = iter(records)
        sorter = SortReader(reader, key)
        assert list(sorter) == sorted(records, key=key)
        return

    def test_iter_group(self, records):
        """ Test the iterator protocol with grouping.

        """
        key = "num"
        group = "mod"
        reader = iter(iter(sorted(records, key=itemgetter(group))))
        sorter = SortReader(reader, key, group)
        assert list(sorter) == sorted(records, key=itemgetter(group, key))
        return


class SortWriterTest(object):
    """ Unit testing for the SortWriter class.

    """
    def test_write(self, records, writer):
        """ Test the write() and close() methods.

        """
        key = "num"
        sorter = SortWriter(writer, key)
        for record in records:
            sorter.write(record)
        sorter.close()
        sorter.close()  # test that redundant calls are a no-op
        assert writer.output == sorted(records, key=itemgetter(key))
        return

    def test_write_multi(self, records, writer):
        """ Test the write() method with a multi-value key.

        """
        key = "mod", "num"
        sorter = SortWriter(writer, key)
        for record in records:
            sorter.write(record)
        sorter.close()
        assert writer.output == sorted(records, key=itemgetter(*key))
        return

    def test_write_custom_key(self, records, writer):
        """ Test the write() method with a custom key fucntion.

        """
        key = itemgetter("num")
        sorter = SortWriter(writer, key)
        for record in records:
            sorter.write(record)
        sorter.close()
        assert writer.output == sorted(records, key=key)
        return

    def test_write_group(self, records, writer):
        """ Test the write() method with grouping.

        """
        key = "num"
        group = "mod"
        sorter = SortWriter(writer, key, group)
        for record in sorted(records, key=itemgetter(group)):
            sorter.write(record)
        sorter.close()
        assert writer.output == sorted(records, key=itemgetter(group, key))
        return

    def test_dump(self, records, writer):
        """ Test the dump() method.

        """
        key = "num"
        sorter = SortWriter(writer, key)
        sorter.dump(records)
        assert writer.output == sorted(records, key=itemgetter(key))
        return


# Make the module executable.

if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))

