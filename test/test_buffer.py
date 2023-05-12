""" Testing for the the buffer.py module

The script can be executed on its own or incorporated into a larger test suite.
However the tests are run, be aware of which version of the module is actually
being tested. If the library is installed in site-packages, that version takes
precedence over the version in this project directory. Use a virtualenv test
environment or setuptools develop mode to test against the development version.

"""
import pytest

from serial.core.buffer import _ReaderBuffer
from serial.core.buffer import _WriterBuffer


@pytest.fixture
def input():
    """ Return input records.

    """
    return [{"str": "abc"}, {"str": "def"}, {"str": "ghi"}]


@pytest.fixture
def output():
    """ Return output records

    """
    return [{"str": "abcdef"}, {"str": "ghi"}]


def filter(record):
    """ Filter for testing.

    """
    return record if record["str"] != "abcdef" else None


class ReaderBufferTest(object):
    """ Unit testing for the _ReaderBuffer class

    """
    def test_iter(self, input, output):
        """ Test the iterator protocol.

        """
        buffer = ReaderBuffer(iter(input))
        assert list(buffer) == output
        return

    def test_filter(self, input, output):
        """ Test the iterator protocol.

        """
        buffer = ReaderBuffer(iter(input))
        buffer.filter(filter)
        assert list(buffer) == output[1:]
        return


class WriterBufferTest(object):
    """ Unit testing for the _WriterBuffer class.

    """
    def test_write(self, input, output, writer):
        """ Test the write() anc close() methods.

        """
        buffer = WriterBuffer(writer)
        for record in input:
            buffer.write(record)
        buffer.close()
        buffer.close()  # test that redundant calls are a no-op
        assert writer.output == output
        return

    def test_dump(self, input, output, writer):
        """ Test the dump() methods.

        """
        buffer = WriterBuffer(writer)
        buffer.dump(input)
        assert writer.output == output
        return

    def test_filter(self, input, output, writer):
        """ Test the write() anc close() methods.

        """
        buffer = WriterBuffer(writer)
        buffer.filter(filter)
        buffer.dump(input)
        assert writer.output == output[1:]
        return


class ReaderBuffer(_ReaderBuffer):
    """ Concrete implementation of a _ReaderBuffer for testing.

    """
    def __init__(self, reader):
        """ Initialize this object.

        """
        super(ReaderBuffer, self).__init__(reader)
        self._saved = None
        return

    def _queue(self, record):
        """ Merge every two records.

        """
        if not self._saved:
            # First record in a pair.
            self._saved = record
        else:
            # Complete the pair.
            self._saved["str"] += record["str"]
            self._output.append(self._saved)
            self._saved = None
        return

    def _uflow(self):
        """ Handle an underflow condition.

        """
        if self._saved:
            # No more input, so output the last record as-is.
            self._output.append(self._saved)
            self._saved = None
        else:
            raise StopIteration
        return


class WriterBuffer(_WriterBuffer):
    """ Concrete implementation of a _WriterBuffer for testing.

    """
    def __init__(self, writer):
        """ Initialize this object.

        """
        super(WriterBuffer, self).__init__(writer)
        self._saved = None
        return

    def _queue(self, record):
        """ Merge every two records.

        """
        if not self._saved:
            # First record in a pair.
            self._saved = record
        else:
            # Complete the pair.
            self._saved["str"] += record["str"]
            self._output.append(self._saved)
            self._saved = None
        return

    def _flush(self):
        """ Complete any buffering operations.

        """
        if self._saved:
            # No more input, so output the last record as-is.
            self._output.append(self._saved)
        return


# Make the module executable.

if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
