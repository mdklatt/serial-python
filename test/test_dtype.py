""" Testing for the the dtype.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
from datetime import datetime

import _path
import _unittest as unittest

from serial.core import ConstType
from serial.core import IntType
from serial.core import FloatType
from serial.core import StringType
from serial.core import DatetimeType
from serial.core import ArrayType


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class _DataTypeTest(unittest.TestCase):
    """ Base class for DataType unit tests.

    """
    def test_decode(self):
        """ Test the decode() method.

        """
        self.assertEqual(self.value, self.dtype.decode(self.token))
        return

    def test_decode_null(self):
        """ Test the decode() method for null input.

        """
        self.assertEqual(None, self.dtype.decode(" "))
        return

    def test_decode_default(self):
        """ Test the decode() method for a default value.

        """
        self.assertEqual(self.default_value, self.default_dtype.decode(" "))
        return

    def test_encode(self):
        """ Test the encode() method.

        """
        self.assertEqual(self.token, self.dtype.encode(self.value))
        return

    def test_encode_null(self):
        """ Test the encode() method for null output.

        """
        self.assertEqual("", self.dtype.encode(None))
        return

    def test_encode_default(self):
         """ Test the encode() method for a default value.

         """
         self.assertEqual(self.default_token, self.default_dtype.encode(None))
         return


class ConstTypeTest(_DataTypeTest):
    """ Unit testing for the ConstType class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.value = 9999
        self.token = " 9999"
        self.dtype = ConstType(self.value, "5d")
        self.default_value = self.value
        self.default_token = self.token
        self.default_dtype = self.dtype
        return

    # ConstTypes always have a non-null default value.
    test_decode_null = _DataTypeTest.test_decode_default
    test_encode_null = _DataTypeTest.test_encode_default


class IntTypeTest(_DataTypeTest):
    """ Unit testing for the IntType class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        fmt = "4d"
        self.value = 123
        self.token = " 123"
        self.dtype = IntType(fmt)
        self.default_value = -999
        self.default_token = "-999"
        self.default_dtype = IntType(fmt, self.default_value)
        return


class FloatTypeTest(_DataTypeTest):
    """ Unit testing for the FloatType class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        fmt = "6.3f"
        self.value = 1.23
        self.token = " 1.230"
        self.dtype = FloatType(fmt)
        self.default_value = -9.999
        self.default_token = "-9.999"
        self.default_dtype = FloatType(fmt, self.default_value)
        return


class StringTypeTest(_DataTypeTest):
    """ Unit testing for the StringType class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        fmt = "4s"
        self.value = "abc"
        self.token = "abc "
        self.dtype = StringType(fmt)
        self.default_value = "xyz"
        self.default_token = "xyz "
        self.default_dtype = StringType(fmt, default=self.default_value)
        self.quote_token = "'abc'"
        self.quote_dtype = StringType(quote="'")
        return

    def test_decode_quote(self):
        """ Test the decode method() for a quoted string.

        """
        self.assertEqual(self.value, self.quote_dtype.decode(self.quote_token))
        return

    def test_encode_quote(self):
        """ Test the decode method() for a quoted string.

        """
        self.assertEqual(self.quote_token, self.quote_dtype.encode(self.value))
        return

    def test_encode_null(self):
        """ Test the decode() method for null input.

        """
        # Override the base class to test for a fixed-width blank field.
        self.assertEqual(format("", "4s"), self.dtype.encode(None))
        return


class DatetimeTypeTest(_DataTypeTest):
    """ Unit testing for the DatetimeType class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        timefmt = "%Y-%m-%dT%H:%M:%S.%f"
        self.value = datetime(2012, 12, 31, 0, 0, 0, 456000)
        self.token = "2012-12-31T00:00:00.456"
        self.dtype = DatetimeType(timefmt, 3)
        self.default_value = datetime(1901, 1, 1)
        self.default_token = "1901-01-01T00:00:00.000"
        self.default_dtype = DatetimeType(timefmt, 3, self.default_value)
        return


class ArrayTypeTest(_DataTypeTest):
    """ Unit testing for the ArrayType class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        fields =  (("str", 0, StringType()), ("int", 1, IntType()))
        self.dtype = ArrayType(fields)
        self.value = [{"str": "abc", "int": 123}, {"str": "def", "int": 456}]
        self.token = ["abc", "123", "def", "456"]
        return
 
    def test_decode_null(self):
        """ Test the decode() method for null input.

        """
        pass

    def test_decode_default(self):
        """ Test the decode() method for a default value.

        """
        pass

    def test_encode_null(self):
        """ Test the encode() method for null output.

        """
        pass 

    def test_encode_default(self):
        """ Test the encode() method for a default value.

        """
        pass


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
