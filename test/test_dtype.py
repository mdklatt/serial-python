""" Testing for the the dtype.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import _path

import datetime
import unittest

from serial.core import ConstType
from serial.core import IntType
from serial.core import FloatType
from serial.core import StringType
from serial.core import DatetimeType
from serial.core import ArrayType


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class DataTypeTest(unittest.TestCase):
    """ Base class for DataType unit tests.

    """
    def test_decode(self):
        """ Test the decode() method.

        """
        self.assertEqual(self.value, self.field.decode(self.token))
        return

    def test_decode_default(self):
        """ Test the decode() method for default input.

        """
        self.assertEqual(self.default_value, self.field.decode(" "))
        return

    def test_encode(self):
        """ Test the encode() method.

        """
        self.assertEqual(self.token, self.field.encode(self.value))
        return

    def test_encode_default(self):
         """ Test the encode() method for default input.

         """
         self.assertEqual(self.default_token, self.field.encode(None))
         return


class ConstTypeTest(DataTypeTest):
    """ Unit testing for the ConstType class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.value = 999
        self.token = " 999"
        self.default_value = self.value
        self.default_token = self.token
        self.field = ConstType(self.value, "4d")
        return


class IntTypeTest(DataTypeTest):
    """ Unit testing for the IntType class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.value = 123
        self.token = " 123"
        self.default_value = -999
        self.default_token = "-999"
        self.field = IntType("4d", self.default_value)
        return


class FloatTypeTest(DataTypeTest):
    """ Unit testing for the FloatType class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.value = 1.23
        self.token = " 1.23"
        self.default_value = -9.99
        self.default_token = "-9.99"
        self.field = FloatType("5.2f", self.default_value)
        return


class StringTypeTest(DataTypeTest):
    """ Unit testing for the StringType class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.value = "abc"
        self.token = "abc "
        self.default_value = "xyz"
        self.default_token = "xyz "
        self.field = StringType("4s", default=self.default_value)
        return

    def test_decode_quote(self):
        """ Test the decode method() for a quoted string.

        """
        self.value = "abc"
        self.token = "'abc'"
        self.field = StringType("s", "'")
        self.assertEqual(self.value, self.field.decode(self.token))
        return

    def test_encode_quote(self):
        """ Test the decode method() for a quoted string.

        """
        self.value = "abc"
        self.token = "'abc'"
        self.field = StringType("s", "'")
        self.assertEqual(self.token, self.field.encode(self.value))
        return


class DatetimeTypeTest(DataTypeTest):
    """ Unit testing for the DatetimeType class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.value = datetime.datetime(2012, 12, 12, 0, 0, 0, 123000)
        self.token = "2012-12-12T00:00:00.123"
        self.default_value = datetime.datetime(1901, 1, 1)
        self.default_token = "1901-01-01T00:00:00.000"
        self.field = DatetimeType("%Y-%m-%dT%H:%M:%S.%f", 3, self.default_value)
        return


class ArrayTypeTest(unittest.TestCase):
    """ Unit testing for the ArrayType class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        fields = (("A", 0, IntType("2d")), ("B", 1, IntType("2d")))
        self.values = [{"A": 1, "B": 2}, {"A": 3, "B": 4}]
        self.tokens = [" 1", " 2", " 3", " 4"]
        self.field = ArrayType(fields)
        return

    def test_decode(self):
        """ Test the decode() method.

        """
        self.assertEqual(self.values, self.field.decode(self.tokens))
        return

    def test_encode(self):
        """ Test the encode() method.

        """
        self.assertEqual(self.tokens, self.field.encode(self.values))
        return


# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (ConstTypeTest, IntTypeTest, FloatTypeTest, StringTypeTest,
               DatetimeTypeTest, ArrayTypeTest)

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
