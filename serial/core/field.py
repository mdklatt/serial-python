""" Data fields convert text tokens to/from Python types. 

Client code defines the field type for each input/ouput field, but the _Reader
and _Writer classes are responsible for using them.

"""
from __future__ import absolute_import

from datetime import datetime
from itertools import product

from ._util import TimeFormat


__all__ = ("ConstField", "IntField", "FloatField", "StringField", 
           "DatetimeField", "ArrayField")


class _ScalarField(object):
    """ Base class for scalar field types.

    """
    def __init__(self, name, pos):
        """ Initialize this object.

        """
        # The field width is in units appropriate to the file type, e.g. 
        # characters for fixed-width data or fields for delimited data.    
        self.name = name
        try:
            self.pos = slice(*pos)
            self.width = self.pos.stop - self.pos.start
        except TypeError:  # pos is an int
            self.pos = pos
            self.width = 1
        return

    def decode(self, token):
        """ Convert input to a Python value.

        This is called by a Reader while parsing an input record.

        """
        raise NotImplementedError
        
    def encode(self, value):
        """ Convert a Python value to output
        
        This is called by a Wrier while formatting an output record.
        
        """
        raise NotImplementedError


class ConstField(_ScalarField):
    """ A constant value field.

    """
    def __init__(self, name, pos, value, fmt="s"):
        """ Initialize this object.

        """
        super(ConstField, self).__init__(name, pos)
        self._value = value
        self._token = format(self._value, fmt)
        return

    def decode(self, token):
        """ Return a const value (input is ignored).

        """
        return self._value

    def encode(self, value):
        """ Return a const token (value is ignored).

        """
        return self._token


class IntField(_ScalarField):
    """ An integer field.

    """
    def __init__(self, name, pos, fmt="d", default=None):
        """ Initialize this object.

        """
        super(IntField, self).__init__(name, pos)
        self._fmt = fmt
        self._default = default
        return
        
    def decode(self, token):
        """ Convert a string token to a Python value.
        
        If the token is an empty string the default field value is used.
        
        """
        try:
            value = int(token)
        except ValueError:  # type conversion failed
            value = self._default
        return value
        
    def encode(self, value):
        """ Convert a Python value to a string token.
        
        If the value is None the default field value is used (None is encoded 
        as a null string).
        
        """
        if value is None:
            value = self._default  # may still be None
        return format(value, self._fmt) if value is not None else ""


class FloatField(_ScalarField):
    """ A floating point field.

    """
    def __init__(self, name, pos, fmt="g", default=None):
        """ Initialize this object.

        """
        super(FloatField, self).__init__(name, pos)
        self._fmt = fmt
        self._default = default
        return
        
    def decode(self, token):
        """ Convert a string token to a Python value.
        
        If the token is an empty string the default field value is used.

        """
        try:
            value = float(token)
        except ValueError:  # type conversion failed
            value = self._default
        return value
        
    def encode(self, value):
        """ Convert a Python value to a string token.
        
        If the value is None the default field value is used (None is encoded 
        as a null string).
        
        """
        if value is None:
            value = self._default  # may still be None
        return format(value, self._fmt) if value is not None else ""


class StringField(_ScalarField):
    """ A string field.

    """
    def __init__(self, name, pos, fmt="s", quote="", default=None):
        """ Initialize this object.

        """
        super(StringField, self).__init__(name, pos)
        self._fmt = fmt
        self._quote = quote
        self._default = default
        return

    def decode(self, token):
        """ Convert a string token to a Python value.

        Surrounding whitespace and quotes are removed, and if the resulting
        string is null the default field value is used.

        """
        return token.strip().strip(self._quote) or self._default

    def encode(self, value):
        """ Convert a Python value to a string token.

        If the value is None the default field value is used (None is encoded
        as a null string).

        """
        value = value or self._default or ""
        return "{0:s}{1:s}{0:s}".format(self._quote, format(value, self._fmt))


class DatetimeField(_ScalarField):
    """ A datetime field.

    """
    def __init__(self, name, pos, fmt, prec=0, default=None):
        """ Initialize this object.

        The precision argument specifies precision to use for fractional
        seconds during encoding (the full available precision is used for
        decoding).

        """
        super(DatetimeField, self).__init__(name, pos)
        self._fmtstr = fmt
        self._fmtobj = TimeFormat(self._fmtstr)
        self._prec = min(max(prec, 0), 6)  # max precision is microseconds
        self._default = default
        return

    def decode(self, token):
        """ Convert a string token to a Python value.

        """
        token = token.strip()
        if not token:
            return self._default
        return datetime.strptime(token, self._fmtstr)

    def encode(self, value):
        """ Convert a Python value to a string token.

        If the value is None the default field value is used (None is encoded 
        as a null string).

        """
        value = value or self._default
        if value is None:
            return ""
        token = self._fmtobj(value)
        if (self._prec > 0):
            time, usecs = token.split(".")
            token = "{0:s}.{1:s}".format(time, usecs[0:self._prec])
        return token


class ArrayField(object):
    """ An array of composite field elements.

    """
    def __init__(self, name, pos, fields, default=None):
        """ Initialize this object.

        """
        self.name = name
        self.pos = slice(*pos)
        try:
            self.width = self.pos.stop - self.pos.start
        except TypeError:  # pos.stop is None
            # This is a variable-width field; width needs to be determined
            # during decoding or encoding.
            self.width = None
        self._fields = fields
        self._stride = sum(field.width for field in self._fields)
        self._default = default
        return

    def decode(self, tokens):
        """ Convert a sequence of string tokens to a list of Python values.

        This works for sequences of strings (e.g. from DelimitedReader) or a 
        string as a sequence (e.g. from FixedWidthReader). Each Python value
        is a list of elements where each element is a dict corresponding to
        the fields defined for the array.
        
        """
        def parse():
            """ Split input into array elements. """
            # If the length of the input array is not a multiple of _stride the
            # last element will be incomplete.
            for beg in xrange(0, len(tokens), self._stride):
                end = beg + self._stride
                yield tokens[beg:end]
            return        
        
        values = []
        for elem in parse():
            # Decode the fields in each element into a dict.
            elem = dict((field.name, field.decode(elem[field.pos])) for field 
                        in self._fields)
            values.append(elem)
        values = values or self._default or []
        if self.width is None:
            # Update the width of a variable-length array with each record.
            self.width = len(values) * self._stride
        return values

    def encode(self, values):
        """ Convert a sequence of Python values to a list of string tokens.

        If the value is None or an empty sequence the default field value is
        used (None is encoded as an empty list). Each element of the array 
        should be a dict-like object that corresponds to the field definitions 
        for this array.

        """
        values = values or self._default or []
        if self.width is None:
            # Update the width of a variable-length array with each record.
            self.width = len(values) * self._stride
        return [field.encode(elem.get(field.name)) for elem, field in
                product(values, self._fields)]
