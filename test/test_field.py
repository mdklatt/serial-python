""" Testing for the the field.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
from datetime import datetime
from itertools import izip

import _path
import _unittest as unittest

from serial.core.field import *  # test __all__


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.

class _FieldTest(unittest.TestCase):
    """ Unit testing for data field classes.

    This is an abstract class and should not be called directly by any test
    runners.

    """
    def test_init(self):
        """ Test the __init__() method. 
        
        """
        self.assertEqual(self.name, self.field.name)
        self.assertEqual(slice(*self.pos), self.field.pos)
        self.assertEqual(self.width, self.field.width)
        return
    
    def test_decode(self):
        """ Test the decode() method.

        """
        self.assertEqual(self.value, self.field.decode(self.token))
        return

    def test_decode_null(self):
        """ Test the decode() method for null input.

        """
        self.assertEqual(None, self.field.decode(" "))
        return

    def test_decode_default(self):
        """ Test the decode() method for a default value.

        """
        self.assertEqual(self.default_value, self.default_field.decode(" "))
        return

    def test_encode(self):
        """ Test the encode() method.

        """
        self.assertEqual(self.token, self.field.encode(self.value))
        return

    def test_encode_null(self):
        """ Test the encode() method for null output.

        """
        # This only works for fixed-width fields.
        self.assertEqual(" ".rjust(self.field.width), self.field.encode(None))
        return

    def test_encode_default(self):
         """ Test the encode() method for a default value.

         """
         self.assertEqual(self.default_token, self.default_field.encode(None))
         return


class ConstFieldTest(_FieldTest):
    """ Unit testing for the ConstField class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.name = "const"
        self.pos = 1, 6
        self.width = 5
        self.value = 9999
        self.token = " 9999"
        self.field = ConstField(self.name, self.pos, self.value, "5d")
        self.default_value = self.value
        self.default_token = self.token
        self.default_field = self.field
        return

    # ConstFields always have a non-null default value.
    test_decode_null = _FieldTest.test_decode_default
    test_encode_null = _FieldTest.test_encode_default


class IntFieldTest(_FieldTest):
    """ Unit testing for the IntField class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        fmt = "4d"
        self.name = "int"
        self.pos = 1, 5
        self.width = 4
        self.value = 123
        self.token = " 123"
        self.field = IntField(self.name, self.pos, fmt)
        self.default_value = -999
        self.default_token = "-999"
        self.default_field = IntField(self.name, self.pos, fmt, 
                                      self.default_value)
        return


class FloatFieldTest(_FieldTest):
    """ Unit testing for the FloatField class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        fmt = "6.3f"
        self.name = "int"
        self.pos = 1, 7
        self.width = 6
        self.value = 1.23
        self.token = " 1.230"
        self.field = FloatField(self.name, self.pos, fmt)
        self.default_value = -9.999
        self.default_token = "-9.999"
        self.default_field = FloatField(self.name, self.pos, fmt, 
                                        self.default_value)
        return


class StringFieldTest(_FieldTest):
    """ Unit testing for the StringField class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        fmt = "5s"
        self.name = "string"
        self.pos = 1, 6
        self.width = 5
        self.value = "abc"
        self.token = "abc  "
        self.field = StringField(self.name, self.pos, fmt)
        self.default_value = "xyz"
        self.default_token = "xyz  "
        self.default_field = StringField(self.name, self.pos, fmt, 
                                         default=self.default_value)
        self.quote_token = "'abc'"
        self.quote_field = StringField(self.name, self.pos, quote="'")
        return

    def test_decode_quote(self):
        """ Test the decode method() for a quoted string.

        """
        self.assertEqual(self.value, self.quote_field.decode(self.quote_token))
        return

    def test_encode_quote(self):
        """ Test the decode method() for a quoted string.

        """
        self.assertEqual(self.quote_token, self.quote_field.encode(self.value))
        return


class DatetimeFieldTest(_FieldTest):
    """ Unit testing for the DatetimeField class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        fmt = "%Y-%m-%dT%H:%M:%S.%f"
        self.name = "datetime"
        self.pos = 1, 24
        self.width = 23
        self.value = datetime(2012, 12, 31, 0, 0, 0, 456000)
        self.token = "2012-12-31T00:00:00.456"
        self.field = DatetimeField(self.name, self.pos, fmt, 3)
        self.default_value = datetime(1801, 1, 1)  # test "old" date
        self.default_token = "1801-01-01T00:00:00.000"
        self.default_field = DatetimeField(self.name, self.pos, fmt, 3, 
                                           self.default_value)
        return
    
    
class ArrayFieldTest(_FieldTest):
    """ Unit testing for the ArrayField class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        array_fields =  (StringField("str", 0), IntField("int", 1))
        self.name = "array"
        self.pos = 1, 5 
        self.width = 4
        self.value = [{"str": "abc", "int": 123}, {"str": "def", "int": 456}]
        self.token = ["abc", "123", "def", "456"]
        self.field = ArrayField(self.name, self.pos, array_fields)
        self.default_value = [{"str": "xyz", "int": -999}]
        self.default_token = ["xyz", "-999"]
        self.default_field = ArrayField(self.name, self.pos, array_fields, 
                                        self.default_value)
        return
 
    def test_decode_null(self):
        """ Test the decode() method for null input.

        """
        self.assertEqual([], self.field.decode([]))
        return

    def test_decode_default(self):
        """ Test the decode() method for a default value.
    
        """
        self.assertEqual(self.default_value, self.default_field.decode([]))
        return

    def test_encode_null(self):
        """ Test the encode() method for null output.
    
        """
        self.assertEqual([], self.field.encode([]))
        return

    def test_encode_default(self):
        """ Test the encode() method for a default value.
    
        """
        self.assertEqual(self.default_token, self.default_field.encode([]))
        return


class RecordFieldTest(ArrayFieldTest):
    """ Unit testing for the RecordField class.
    
    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.fields = (
            StringField("str", 0, default="xyz"), 
            IntField("int", 1, default=-999))
        self.name = "record"
        self.pos = 1, 3 
        self.width = 2
        self.value = {"str": "abc", "int": 123}
        self.token = ["abc", "123"]
        self.field = RecordField(self.name, self.pos, self.fields)
        self.default_value = {"str": "xyz", "int": -999}
        self.default_token = ["xyz", "-999"]
        self.default_field = RecordField(self.name, self.pos, self.fields, 
                                         self.default_value)
        return

    def test_decode_null(self):
        """ Test the decode() method for null input.
    
        """
        self.assertEqual(self.default_value, self.field.decode([]))
        return
    
    def test_encode_null(self):
        """ Test the encode() method for null output.
    
        """
        self.assertEqual(self.default_token, self.field.encode([]))
        return


# Specify the test cases to run for this module (disables automatic discovery).

_TEST_CASES = (ConstFieldTest, IntFieldTest, FloatFieldTest, StringFieldTest,
               DatetimeFieldTest, RecordFieldTest, ArrayFieldTest)

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
