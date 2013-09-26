""" Data types convert text tokens to/from Python types.

Client code defines the _DataType for each input/ouput field, but the _Reader
and _Writer classes are responsible for actually using them.

"""
from __future__ import absolute_import

from datetime import datetime
from itertools import product

from ._util import Field
from ._util import TimeFormat


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
        if value is None:  # need explict None test
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
        return token.strip().strip(self._quote) or self._default

    def encode(self, value):
        """ Convert a string to a text token.

        If value is None the default value for this field is used. A default
        value of None is encoded as a blank string (with quoting if enabled).

        """
        value = value or self._default or ""
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
        self._fmtstr = timefmt
        self._fmtobj = TimeFormat(timefmt)
        self._prec = min(max(prec, 0), 6)  # max precision is microseconds
        return

    def decode(self, token):
        """ Convert a text token to a datetime.

        """
        token = token.strip()
        if not token:
            return self._default
        return datetime.strptime(token, self._fmtstr)

    def encode(self, value):
        """ Convert a datetime to a text token.

        If value is None the default value for this field is used. A default
        value of None is encoded as a blank string.

        """
        value = value or self._default
        if value is None:
            return ""
        token = self._fmtobj(value)
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
        super(ArrayType, self).__init__(list, None, default)
        self.width = None
        self._fields = []
        self._stride = 0
        for name, pos, dtype in fields:
            field = Field(name, pos, dtype)
            self._fields.append(field)
            self._stride += field.width
        return

    def decode(self, token_array):
        """ Convert a sequence of text tokens to an array of values.

        This works for sequences of strings (e.g. from DelimitedReader) or a 
        string as a sequence (e.g. from FixedWidthReader). Each decoded value
        is an array of elements where each element is a dict corresponding to
        the fields defined for this array.
        
        """
        def parse():
            """ Split token_array into array elements. """
        
            # If the length of the input array is not a multiple of _stride the
            # last element will be incomplete.
            for beg in xrange(0, len(token_array), self._stride):
                end = beg + self._stride
                yield token_array[beg:end]
            return        
        
        value_array = []
        for elem in parse():
            # Decode the fields in each element into a dict.
            values = dict((field.name, field.dtype.decode(elem[field.pos]))
                          for field in self._fields)
            value_array.append(values)
        value_array = value_array or self._default
        self.width = len(value_array) * self._stride
        return value_array

    def encode(self, value_array):
        """ Convert an array of values to a sequence of text tokens.

        If value_array is an empty sequence the default value for this field is 
        used. Each element of the array should be a dict-like object that
        corresponds to the field definitions for this array.

        """
        value_array = value_array or self._default
        self.width = len(value_array) * self._stride
        return [field.dtype.encode(elem.get(field.name)) for elem, field in
                product(value_array, self._fields)]
