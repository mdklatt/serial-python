""" Testing for the the writer.py module

The script can be executed on its own or incorporated into a larger test suite.
However the tests are run, be aware of which version of the module is actually
being tested. If the library is installed in site-packages, that version takes
precedence over the version in this project directory. Use a virtualenv test
environment or setuptools develop mode to test against the development version.

"""
from contextlib import closing
from gzip import GzipFile
from io import BytesIO
from zlib import compress

import pytest

from serial.core.stream import *  # tests __all__


@pytest.fixture
def lines():
    """ Return lines of test data.

    """
    return ["abc\n", "def\n", "ghi\n"]


def zlib_stream(data):
    """ Return test data as a zlib-compressed stream.

    """
    return BytesIO(compress(data))

def gzip_stream(data):
    """ Return data as a gzip-compressed stream.

    """
    stream = BytesIO()
    with closing(GzipFile(fileobj=stream, mode="w")) as writer:
        # Explicit closing() context is necessary for Python 2.6 but not for
        # 2.7. Closing the GzipFile doesn't close its fileobj.
        writer.write(data)
    stream.seek(0)  # rewind for reading
    return stream


class _IStreamTest(object):
    """ Abstract base class for input stream adaptor unit testing.

    """
    def test_next(self, stream, lines):
        """ Test the __next__() method.

        """
        assert next(stream) == lines[0]

    def test_iter(self, stream, lines):
        """ Test the __iter__() method.

        """
        assert list(stream) == lines
        return

    def test_close(self, stream):
        """ Test the close() method.

        """
        stream.close()
        with pytest.raises(ValueError) as exinfo:
            next(stream)
        assert "closed file" in str(exinfo.value)
        return


class BufferedIStreamTest(_IStreamTest):
    """ Unit testing for the BufferedIStream class.

    """
    BUFLEN = 2

    @classmethod
    @pytest.fixture
    def stream(cls, lines):
        """ Return a test data stream.

        """
        return BufferedIStream(BytesIO("".join(lines)), cls.BUFLEN)

    def test_rewind(self, stream, lines):
        """ Test the rewind() method.

        """
        for _ in range(self.BUFLEN):
            # Stay within the buffer limits.
            next(stream)
        stream.rewind(self.BUFLEN)
        assert list(stream) == lines

    def test_rewind_limit(self, stream, lines):
        """ Test the limits of the rewind method.

        """
        list(stream)
        stream.rewind()  # beginning of buffer, not stream
        assert list(stream) == lines[-self.BUFLEN:]
        return


class FilteredIStreamTest(_IStreamTest):
    """ Unit testing for the FilteredIStream class.

    """
    @classmethod
    @pytest.fixture
    def stream(cls, lines):
        """ Return a test data stream.

        """
        return FilteredIStream(BytesIO("".join(lines)))

    def test_filter(self, stream, lines):
        """ Test the filter method.

        """
        def stop_filter(line):
            """ Stop iteration. """
            if line.rstrip() == "ghi":
                raise StopIteration
            return line

        def reject_filter(line):
            """ Reject a line. """
            return line if line.rstrip() != "abc" else None

        stream.filter(stop_filter, reject_filter)
        assert list(stream) == lines[1:2]


class GzippedIStreamTest(_IStreamTest):
    """ Unit testing for the GzippedIStream class.

    """
    @pytest.fixture
    def lines(self):
        """ Return lines of test data.

        """
        # Test blank lines, lines longer, shorter, and equal to the block size,
        # and no trailing \n.
        GzippedIStream.block_size = 4
        return ["\n", "abcdefgh\n", "ijkl"]

    @classmethod
    @pytest.fixture(params=(gzip_stream, zlib_stream))
    def stream(cls, request, lines):
        """ Return a test data stream.

        """
        open = request.param
        return GzippedIStream(open("".join(lines)))


class FilteredOStreamTest(object):
    """ Unit testing for the FilteredOStream class.

    """
    def test_write(self, lines):
        """ Test the write() method.

        """
        stream = BytesIO()
        writer = FilteredOStream(stream)
        for line in lines:
            writer.write(line)
        assert stream.getvalue() == "".join(lines)

    def test_filter(self, lines):
        """ Test the filter() method.

        """
        def reject_filter(line):
            """ Reject a line. """
            return line if line.rstrip() != "ABC" else None

        def modify_filter(line):
            """ Modify a line. """
            return line.lower()

        stream = BytesIO()
        writer = FilteredOStream(stream)
        writer.filter(reject_filter, modify_filter)
        for line in lines:
            writer.write(line.upper())
        assert stream.getvalue() == "".join(lines[1:])

    def test_close(self, lines):
        """ Test the close() method.

        """
        stream = FilteredOStream(BytesIO())
        stream.close()
        with pytest.raises(ValueError) as exinfo:
            stream.write(lines[0])
        assert "closed file" in str(exinfo.value)
        return


# Make the module executable.

if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
