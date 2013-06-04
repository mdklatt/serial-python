""" Data types for converting text tokens to/from Python types.

Client code defines the _DataType for each input/ouput field, but the _Reader
and _Writer classes are responsible for calling decode() and encode().

"""
from collections import namedtuple
from datetime import datetime
from itertools import product

from ._util import strftime


__all__ = ("ConstType", "IntType", "FloatType", "StringType", "DatetimeType",
           "ArrayType")


class _DataType(object):
    """ Base class for data types.

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

        If value is None the default value for this field is used. A default
        value of None is encoded as a blank string.
        
        """
        if value is None:
            value = self._default
        return format(value, self._fmt) if value is not None else ""


class ConstType(_DataType):
    """ A constant value.

    """
    def __init__(self, value, fmt="s"):
        """ Initialize this object.

        """
        super(ConstType, self).__init__(type(value), fmt, value)
        return

    def decode(self, token):
        """ Return a const value (token is ignored).

        """
        return self._default

    def encode(self, value):
        """ Return a const value as a text token (value is ignored).

        """
        return format(self._default, self._fmt)


class IntType(_DataType):
    """ An integer value.

    """
    def __init__(self, fmt="d", default=None):
        """ Initialize this object.

        """
        super(IntType, self).__init__(int, fmt, default)
        return


class FloatType(_DataType):
    """ A floating point value.

    """
    def __init__(self, fmt="g", default=None):
        """ Initialize this object.

        """
        super(FloatType, self).__init__(float, fmt, default)
        return


class StringType(_DataType):
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

        If value is None the default value for this field is used. A default
        value of None is encoded as a blank string (with quoting if enabled).

        """
        if value is None:
            value = self._default if self._default is not None else ""
        return "{0:s}{1:s}{0:s}".format(self._quote, format(value, self._fmt))


class DatetimeType(_DataType):
    """ A datetime value.

    """
    def __init__(self, timefmt, prec=0, default=None):
        """ Initialize this object.

        The precision argument specifies precision to use for fractional
        seconds during encoding (the full available precision is used for
        decoding).

        """
        super(DatetimeType, self).__init__(datetime, "s", default)
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

        If value is None the default value for this field is used. A default
        value of None is encoded as a blank string.

        """
        if value is None:
            if self._default is None:
                return ""
            value = self._default
        token = strftime(value, self._timefmt)
        if (self._prec > 0):
            time, usecs = token.split(".")
            token = "{0:s}.{1:s}".format(time, usecs[0:self._prec])
        return token


class ArrayType(_DataType):
    """ An array of _DataTypes.

    """
    def __init__(self, fields, default=list()):
        """ Initialize this object.

        """
        super(ArrayType, self).__init__(list, "s", default)
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

        If value is not a non-empty sequence the default value for this field 
        is used.

        """
        if not array:
            array = self._default
        return [field.dtype.encode(elem.get(field.name)) for elem, field in
                product(array, self._fields)]
