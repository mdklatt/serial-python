""" Test suite for the the filter.py module

The script can be executed on its own or incorporated into a larger test suite.
However the tests are run, be aware of which version of the module is actually
being tested. If the library is installed in site-packages, that version takes
precedence over the version in this project directory. Use a virtualenv test
environment or setuptools develop mode to test against the development version.

"""
from itertools import izip

import pytest

from serial.core.filter import *  # tests __all__


def pytest_generate_tests(metafunc):
    """ Define a 'data' fixture with custom parameterization.

    """
    if "data" in metafunc.fixturenames:
        # This is the only way to parametrize a class/instance attribute.
        metafunc.parametrize("data", metafunc.cls.data())
    return


class _RecordFilterTest(object):
    """ Abstract base class for testing record filters.

    """
    _DATA = None  # must be defined by derived classes

    @classmethod
    def data(cls):
        """ Return test data for this class.

        """
        keys = "value", "accept"
        return (dict(izip(keys, item)) for item in cls._DATA)

    def test_call(self, testobj, data):
        """ Test the __call__ method for each test record and blacklist option.

        """
        filter, blacklist = testobj
        expect = data if data["accept"] is not blacklist else None
        assert expect == filter(data)
        return

    def test_call_missing(self, testobj, data):
        """ Test the __call__ method for each test record and blacklist option.

        """
        filter, blacklist = testobj
        data = data.copy()  # record is NOT test-independent
        del data["value"]
        expect = data if blacklist else None
        assert expect == filter(data)
        return


class BoolFilterTest(_RecordFilterTest):
    """ Unit testing for the BoolFilter class.

    """
    _DATA = (1, True), (False, False), ("", False), (None, False)

    @pytest.fixture(params=(False, True))
    def testobj(self, request):
        """ Construct a BoolFilter for testing.

        """
        blacklist = request.param
        return BoolFilter("value", blacklist), blacklist


class FieldFilterTest(_RecordFilterTest):
    """ Unit testing for the FieldFilter class.

    """
    _DATA = ("abc", True), ("def", False)

    @pytest.fixture(params=(False, True))
    def testobj(self, request):
        """ Construct a FieldFilter for testing.

        """
        values = (value for value, accept in self._DATA if accept)
        blacklist = request.param
        return FieldFilter("value", values, blacklist), blacklist


class RangeFilterTest(_RecordFilterTest):
    """ Unit testing for the RangeFilter class.

    """
    _DATA = (1, True), (2, False)

    @pytest.fixture(params=(False, True))
    def testobj(self, request):
        """ Construct a RangeFilter for testing.

        """
        blacklist = request.param
        return RangeFilter("value", 1, 2, blacklist), blacklist

    @pytest.mark.parametrize(("start", "stop"), ((None, 2), (1, None)))
    def test_call_limits(self, data, start, stop):
        """ Test the __call__() method with default limits.

        """
        filter = RangeFilter("value", start, stop)
        if start is None:
            expect = data if data["value"] < stop else None
        elif stop is None:
            expect = data if start <= data["value"] else None
        else:
            assert False  # shouldn't get here
        assert expect == filter(data)
        return


class _TextFilterTest(object):
    """ Abstract base class for testing text filters.

    """
    _DATA = ("abc", True), ("def", False)

    @classmethod
    def data(cls):
        """ Return test data for this class.

        """
        keys = "text", "accept"
        return (dict(izip(keys, item)) for item in cls._DATA)

    def test_call(self, testobj, data):
        """ Test the __call__ method for each test string and blacklist option.

        """
        filter, blacklist = testobj
        text = data["text"]
        expect = text if data["accept"] is not blacklist else None
        assert expect == filter(text)
        return


class RegexFilterTest(_TextFilterTest):
    """ Unit testing for the RegexFilter class.

    """
    @pytest.fixture(params=(False, True))
    def testobj(self, request):
        """ Construct a RegexFilter for testing.

        """
        blacklist = request.param
        return RegexFilter("abc", blacklist), blacklist


class SliceFilterTest(_TextFilterTest):
    """ Unit testing for the RegexFilter class.

    """
    @pytest.fixture(params=(False, True))
    def testobj(self, request):
        """ Construct a SliceFilter for testing.

        """
        substr = slice(1, 3)
        values = (text[substr] for text, accept in self._DATA if accept)
        blacklist = request.param
        return SliceFilter(substr, values, blacklist), blacklist


# Make the module executable.

if __name__ == "__main__":
    raise SystemExit(pytest.main(__file__))

