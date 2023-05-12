""" Testing for the the cache.py module

The script can be executed on its own or incorporated into a larger test suite.
However the tests are run, be aware of which version of the module is actually
being tested. If the library is installed in site-packages, that version takes
precedence over the version in this project directory. Use a virtualenv test
environment or setuptools develop mode to test against the development version.

"""
import pytest

from serial.core.cache import *  # tests __all__


class CacheReaderTest(object):
    """ Unit testing for the CacheReader class.

    """
    @pytest.mark.parametrize("data", ([], [0, 1]))
    def test_iter(self, data):
        """ Test the iterator protocol.

        """
        reader = CacheReader(iter(data))
        assert list(reader) == data
        return

    @pytest.mark.parametrize("count", (None, 1))
    def test_rewind(self, count):
        """ Test the rewind() method.

        """
        data = [0, 1]
        reader = CacheReader(iter(data))
        list(reader)  # exhaust reader
        reader.rewind(count)
        expect = data if count is None else data[-count:]
        assert list(reader) == expect
        return

    def test_rewind_maxlen(self):
        """ Test the rewind() method with a maxlen parameter.

        """
        data = [0, 1, 2]
        maxlen = len(data) - 1
        reader = CacheReader(iter(data), maxlen)
        list(reader)  # exhaust reader
        reader.rewind()
        assert list(reader) == data[-maxlen:]
        return


# Make the module executable.

if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))

