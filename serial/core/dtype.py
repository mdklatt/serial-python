""" Data types.

Data types are responsible for converting text tokens to/from Python values.

"""
from collections import namedtuple
from datetime import datetime
from itertools import product

from ._util import strftime


__all__ = ("ConstType", "IntType", "FloatType", "StringType", "DatetimeType",
           "ArrayType")


class DataType(object):
    """ Base class for all data types.

    """
    def __init__(self, dtype, fmt, default):
        """ Initialize this object.

        The dtype argument is the Python data type for this type, fmt is a
        Python format string (e.g. '>10s'), and default is used for missing
        input/output fields. For fixed-width fields fmt *must* specify the
        field width.

        """
        self._dtype = dtype
        self._fmt = fmt
        self._default = default
        return

    def decode(self, token):
        """ Convert a text token to a Python value.

        """
        try:
            value = self._dtype(token.strip())
        except ValueError:  # type conversion failed
            value = self._default
        return value

    def encode(self, value):
        """ Convert a Python value to a text token.

        """
        if value is None:
            if self._default is None:
                raise ValueError("value is None and has no default")
            value = self._default
        return format(value, self._fmt)


class ConstType(DataType):
    """ A constant value.

    """
    def __init__(self, const, fmt="s"):
        """ Initialize this object.

        """
        super(ConstType, self).__init__(type(const), fmt, const)
        self._const = const
        return

    def decode(self, token):
        """ Return a const value (token is ignored).

        """
        return self._const

    def encode(self, value):
        """ Return a const value as a text token (value is ignored).

        """
        return format(self._const, self._fmt)


class IntType(DataType):
    """ An integer value.

    """
    def __init__(self, fmt="d", default=None):
        """ Initialize this object.

        """
        super(IntType, self).__init__(int, fmt, default)
        return


class FloatType(DataType):
    """ A floating point value.

    """
    def __init__(self, fmt="g", default=None):
        """ Initialize this object.

        """
        super(FloatType, self).__init__(float, fmt, default)
        return


class StringType(DataType):
    """ A string value.

    """
    def __init__(self, fmt="s", quote="", default=None):
        """ Initialize this object.

        """
        super(StringType, self).__init__(str, fmt, default)
        self._quote = quote
        return

    def decode(self, token):
        """ Convert a text token to a string.

        """
        value = token.strip().strip(self._quote)
        if not value:
            value = self._default
        return value

    def encode(self, value):
        """ Convert a string to a text token.

        """
        if value is None:
            if self._default is None:
                raise ValueError("required field is missing")
            value = self._default
        return "{0:s}{1:s}{0:s}".format(self._quote, format(value, self._fmt))


class DatetimeType(DataType):
    """ A datetime value.

    """
    def __init__(self, timefmt, prec=0, default=None):
        """ Initialize this object.

        The precision argument specifies precision to use for fractional
        seconds during encoding (the full available precision is used for
        decoding).

        """
        super(DatetimeType, self).__init__(datetime, "{0:s}", default)
        self._timefmt = timefmt
        self._prec = min(max(prec, 0), 6)  # max precision is microseconds
        return

    def decode(self, token):
        """ Convert a text token to a datetime.

        """
        token = token.strip()
        if not token:
            value = self._default
        else:
            value = datetime.strptime(token, self._timefmt)
        return value

    def encode(self, value):
        """ Convert a datetime to a text token.

        """
        if value is None:
            if self._default is None:
                raise ValueError("required field is missing")
            value = self._default
        token = strftime(value, self._timefmt)
        if (self._prec > 0):
            time, usecs = token.split(".")
            token = "{0:s}.{1:s}".format(time, usecs[0:self._prec])
        return token


class ArrayType(DataType):
    """ An array of DataTypes.

    """
    def __init__(self, fields, default=None):
        """ Initialize this object.

        """
        super(ArrayType, self).__init__(list, "{0:s}", default)
        Field = namedtuple("Field", ("name", "pos", "dtype"))
        self._fields = []
        self._elem_width = 0
        for name, pos, dtype in fields:
            try:
                pos = slice(*pos)
                self._elem_width += pos.stop - pos.start
            except TypeError:  # pos is an int
                self._elem_width += 1
            self._fields.append(Field(name, pos, dtype))
        return

    def decode(self, tokens):
        """ Convert a sequence of text tokens to an array of values.

        """
        array = []
        for pos in range(0, len(tokens), self._elem_width):
            elem = tokens[pos:pos+self._elem_width]
            values = dict([(field.name, field.dtype.decode(elem[field.pos]))
                           for field in self._fields])
            array.append(values)
        return array

    def encode(self, array):
        """ Convert an array of values to a sequence of text tokens.

        """
        if not array:
            if self._default is None:
                raise ValueError("required field is missing")
            array = self._default
        return [field.dtype.encode(elem.get(field.name)) for elem, field in
                product(array, self._fields)]
