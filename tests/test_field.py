""" Testing for the the field.py module

The script can be executed on its own or incorporated into a larger test suite.
However the tests are run, be aware of which version of the module is actually
being tested. If the library is installed in site-packages, that version takes
precedence over the version in this project directory. Use a virtualenv test
environment or setuptools develop mode to test against the development version.

"""
from datetime import datetime
from warnings import simplefilter

import pytest
from serial.core.field import *  # tests __all__


class ConstFieldTest(object):
    """ Unit testing for the ConstField class.

    """
    @pytest.mark.parametrize(("pos", "width"), [(0, 1), ((0, 4), 4)])
    def test_init(self, pos, width):
        """ Tess the __init__() method.

        """
        field = ConstField(__name__, pos, 123)
        assert field.name == __name__
        assert field.pos == pos or field.pos == slice(*pos)
        assert field.width == width
        return

    @pytest.mark.parametrize("token", (None, "", "123", "ABC"))
    def test_decode(self, token):
        """ Test the decode method.

        """
        field = ConstField("const", 0, 123)
        assert field.decode(token) == 123
        return

    @pytest.mark.parametrize("value", [None, 123, "ABC"])
    @pytest.mark.parametrize(("pos", "fmt", "token"), [
        (0, None, "123"),
        ((0, 4), "d", " 123"),
        ((0, 4), "05d", "0012")])
    def test_encode(self, pos, fmt, value, token):
        """ Test the encode method.

        """
        field = ConstField("const", pos, 123, fmt)
        assert field.encode(value) == token
        return


class IntFieldTest(object):
    """ Unit testing for the IntField class.

    """
    @pytest.mark.parametrize(("pos", "width"), [(0, 1), ((0, 4), 4)])
    def test_init(self, pos, width):
        """ Tess the __init__() method.

        """
        field = IntField(__name__, pos)
        assert field.name == __name__
        assert field.pos == pos or field.pos == slice(*pos)
        assert field.width == width
        return

    @pytest.mark.parametrize(("token", "value"), [
        (" ", -999),
        ("123", 123)])
    def test_decode(self, token, value):
        """ Test the decode method.

        """
        # TODO: Need to test default value for 'default'.
        field = IntField(__name__, 0, default=-999)
        assert field.decode(token) == value
        return

    @pytest.mark.parametrize(("pos", "fmt", "value", "token"), [
        (0, "d", None, "-999"),
        (0, "4d", 123, " 123"),
        ((0, 4), "d", None, "-999"),
        ((0, 4), "d", 123, " 123"),
        ((0, 4), "05d", 123, "0012")])
    def test_encode(self, pos, fmt, value, token):
        """ Test the encode method.

        """
        # TODO: Need to test default value for 'default'.
        field = IntField(__name__, pos, fmt, default=-999)
        assert field.encode(value) == token
        return


class FloatFieldTest(object):
    """ Unit testing for the FloatField class.

    """
    @pytest.mark.parametrize(("pos", "width"), [(0, 1), ((0, 4), 4)])
    def test_init(self, pos, width):
        """ Tess the __init__() method.

        """
        field = FloatField(__name__, pos)
        assert field.name == __name__
        assert field.pos == pos or field.pos == slice(*pos)
        assert field.width == width
        return

    @pytest.mark.parametrize(("token", "value"), [
        (" ", -999),
        ("1.23", 1.23)])
    def test_decode(self, token, value):
        """ Test the decode method.

        """
        # TODO: Need to test default value for 'default'.
        field = FloatField(__name__, 0, default=-999)
        assert field.decode(token) == value
        return

    @pytest.mark.parametrize(("pos", "fmt", "value", "token"), [
        (0, "g", None, "-999"),
        (0, "6.3f", 1.23, " 1.230"),
        ((0, 4), "f", None, "-999"),
        ((0, 4), "f", 1.23, "1.23"),
        ((0, 4), "5.3f", 1.23, "1.23")])
    def test_encode(self, pos, fmt, value, token):
        """ Test the encode method.

        """
        # TODO: Need to test default value for 'default'.
        field = FloatField(__name__, pos, fmt, default=-999)
        assert field.encode(value) == token
        return


class StringFieldTest(object):
    """ Unit testing for the StringField class.

    """
    @pytest.mark.parametrize(("pos", "width"), [(0, 1), ((0, 4), 4)])
    def test_init(self, pos, width):
        """ Tess the __init__() method.

        """
        field = StringField(__name__, pos)
        assert field.name == __name__
        assert field.pos == pos or field.pos == slice(*pos)
        assert field.width == width
        return

    @pytest.mark.parametrize(("token", "value", "quote"), [
        (" ", "XXX", ""),
        ("''", "XXX", "'"),
        ("' '", " ", "'"),
        ("'ABC'", "ABC", "'")])
    def test_decode(self, token, value, quote):
        """ Test the decode method.

        """
        # TODO: Need to test default value for 'default'.
        field = StringField(__name__, 0, quote=quote, default="XXX")
        assert field.decode(token) == value

    @pytest.mark.parametrize(("pos", "fmt", "quote", "value", "token"), [
        (0, "s", "", None, "XXX"),
        (0, "s", "'", None, "'XXX'"),
        (0, "5s", "'", "ABC", "'ABC  '"),
        ((0, 5), "s", "", None, "  XXX"),
        ((0, 5), "s", "'", None, "'XXX'"),
        ((0, 5), "s", "", "ABC", "  ABC"),
        ((0, 5), "s", "'", "ABC", "'ABC'"),
        ((0, 5), "4s", "'", "ABC", "'ABC ")])
    def test_encode(self, pos, fmt, quote, value, token):
        """ Test the encode method.

        """
        # TODO: Need to test default value for 'default'.
        # TODO: Test quoting.
        field = StringField(__name__, pos, fmt, quote=quote, default="XXX")
        assert field.encode(value) == token
        return


class DatetimeFieldTest(object):
    """ Unit testing for the StringField class.

    """
    TIME = datetime(1980, 11, 6)

    @pytest.mark.parametrize(("pos", "width"), [(0, 1), ((0, 4), 4)])
    def test_init(self, pos, width):
        """ Tess the __init__() method.

        """
        field = DatetimeField(__name__, pos, "%Y")
        assert field.name == __name__
        assert field.pos == pos or field.pos == slice(*pos)
        assert field.width == width
        return

    @pytest.mark.parametrize(("fmt", "token"), [
        ("%Y-%m-%d", "1980-11-06"),
        ("%m/%d/%y", "11/06/80")])
    def test_decode(self, fmt, token):
        """ Test the decode method.

        """
        # TODO: Need to test default value.
        field = DatetimeField(__name__, 0, fmt=fmt)
        assert field.decode(token) == self.TIME
        return

    @pytest.mark.parametrize(("pos", "fmt", "token"), [
        #(0, "s", None, "NULL", ""),
        (0, "%Y-%m-%d", "1980-11-06"),
        # ((0, 11), "s", None, "NULL"),
        ((0, 11), "%Y-%m-%d", " 1980-11-06"),
        ((0, 9), "%Y-%m-%d", "1980-11-0")])
    def test_encode(self, pos, fmt, token):
        """ Test the encode method.

        """
        # TODO: Need to test default value.
        # TODO: Need to test precision.
        field = FloatField(__name__, pos, fmt, default="NULL")
        assert field.encode(self.TIME) == token
        return


class ListFieldTest(object):
    """ Unit testing for the ListField class.

    """
    SUBFIELDS = StringField("str", 0), IntField("int", 1)

    @pytest.mark.parametrize(("pos", "width"), [((0, None), None), ((0, 4), 4)])
    def test_init(self, pos, width):
        """ Tess the __init__() method.

        """
        field = ListField(__name__, pos, self.SUBFIELDS)
        assert field.name == __name__
        assert field.pos == pos or field.pos == slice(*pos)
        assert field.width == width
        return

    def test_decode(self):
        """ Test the decode() method.

        """
        # TODO: Need to test default and null values.
        field = ListField(__name__, (0, 4), self.SUBFIELDS)
        tokens = ["abc", "123", "def", "456"]
        values = [{"str": "abc", "int": 123}, {"str": "def", "int": 456}]
        assert field.decode(tokens) == values
        return

    def test_encode(self):
        """ Test the encode() method.

        """
        # TODO: Need to test default and null values.
        field = ListField(__name__, (0, 4), self.SUBFIELDS)
        tokens = ["abc", "123", "def", "456"]
        values = [{"str": "abc", "int": 123}, {"str": "def", "int": 456}]
        assert field.encode(values) == tokens
        return


class RecordFieldTest(object):
    """ Unit testing for the RecordField class.

    """
    SUBFIELDS = (
        StringField("str", 0, default="XXX"),
        IntField("int", 1, default="-999"))

    def test_init(self):
        """ Tess the __init__() method.

        """
        field = RecordField(__name__, (0, 2), self.SUBFIELDS)
        assert field.name == __name__
        assert field.pos == slice(0, 2)
        assert field.width == 2
        return

    def test_decode(self):
        """ Test the decode() method.

        """
        # TODO: Need to test default and null values.
        field = ListField(__name__, (0, 4), self.SUBFIELDS)
        tokens = ["abc", "123", "def", "456"]
        values = [{"str": "abc", "int": 123}, {"str": "def", "int": 456}]
        assert field.decode(tokens) == values
        return

    def test_encode(self):
        """ Test the encode() method.

        """
        # TODO: Need to test default and null values.
        field = ListField(__name__, (0, 4), self.SUBFIELDS)
        tokens = ["abc", "123", "def", "456"]
        values = [{"str": "abc", "int": 123}, {"str": "def", "int": 456}]
        assert field.encode(values) == tokens
        return


# Make the module executable.

if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
