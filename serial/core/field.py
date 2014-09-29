""" Data fields convert text tokens to/from Python types. 

Client code defines the field type for each input/output field, but the _Reader
and _Writer classes are responsible for using them.

"""
from __future__ import absolute_import

from datetime import datetime
from itertools import product
from warnings import warn

from ._util import TimeFormat


__all__ = ("ConstField", "IntField", "LongField", "FloatField", "StringField", 
           "DatetimeField", "RecordField", "ListField", "ArrayField")


class _ScalarField(object):
    """ Base class for scalar field types. 

    """
    # _ScalarFields are mapped to exactly one input/output token.
    
    def __init__(self, name, pos):
        """ Initialize this object.

        """
        self.name = name
        try:
            self.pos = slice(*pos)
        except TypeError:  # pos is an int
            self.pos = pos
            self.width = 1
            self._fixed = False
        else:
            # This is a fixed-width field; the width is in characters.
            self.width = self.pos.stop - self.pos.start
            self._fixed = True            
        return

    def decode(self, token):
        """ Convert input to a Python value.

        This is called by a Reader while parsing an input record.

        """
        raise NotImplementedError
        
    def encode(self, value):
        """ Convert a Python value to output
        
        This is called by a Writer while formatting an output record.
        
        """
        raise NotImplementedError


class ConstField(_ScalarField):
    """ A constant value field.

    """
    def __init__(self, name, pos, value, fmt=None):
        """ Initialize this object.

        """
        super(ConstField, self).__init__(name, pos)
        self._value = value
        self._token = format(self._value, fmt) if fmt else str(self._value)
        if self._fixed:
            self._token = self._token[:self.width].rjust(self.width)
        return

    def decode(self, token):
        """ Return a constant value (token is ignored).

        """
        return self._value

    def encode(self, value):
        """ Return a constant token (value is ignored).

        """
        return self._token


class _NumericField(_ScalarField):
    """ A numeric field.
    
    """
    _dtype = None  # must be defined by derived classes
    
    def __init__(self, name, pos, fmt, default=None):
        """ Initialize this object.

        """
        super(_NumericField, self).__init__(name, pos)
        self._fmtstr = fmt
        self._default = default
        return
        
    def decode(self, token):
        """ Convert a string token to a Python numeric value.
        
        If the token is an empty string the default field value is used.
        
        """
        try:
            value = self._dtype(token)
        except ValueError:  # type conversion failed
            value = self._default
        return value
        
    def encode(self, value):
        """ Convert a Python numeric value to a string token.
        
        If the value is None the default field value is used (None is encoded 
        as a null string). For fixed-width fields the token is padded on the 
        left or trimmed on the right to fit the allotted width.

        """
        if value is None:
            value = self._default  # may still be None
        token = format(value, self._fmtstr) if value is not None else ""
        return token[:self.width].rjust(self.width) if self._fixed else token
    
    
class IntField(_NumericField):
    """ An integer field.

    The maximum size of an int depends on the underlying platform, i.e. 32-bit
    vs. 64-bit (see sys.maxint). For larger values use a LongField.
    
    """
    _dtype = int
    
    def __init__(self, name, pos, fmt="d", default=None):
        """ Initialize this object.

        """
        super(IntField, self).__init__(name, pos, fmt, default)
        return
 

class LongField(_NumericField):
    """ An unbounded integer field.

    For better performance an IntField should be used if all field values fit 
    into a plain int.
    
    """
    _dtype = long
    
    def __init__(self, name, pos, fmt="d", default=None):
        """ Initialize this object.

        """
        super(LongField, self).__init__(name, pos, fmt, default)
        return

 
class FloatField(_NumericField):
    """ A floating point field.

    """
    _dtype = float
    
    def __init__(self, name, pos, fmt="g", default=None):
        """ Initialize this object.

        """
        super(FloatField, self).__init__(name, pos, fmt, default)
        return
        

class StringField(_ScalarField):
    """ A string field.

    """
    def __init__(self, name, pos, fmt="s", quote="", default=None):
        """ Initialize this object.

        """
        super(StringField, self).__init__(name, pos)
        fmtstr = "{0:s}{{0:{1:s}}}{0:s}".format(quote, fmt)
        self._valfmt = fmtstr.format
        self._quote = quote
        self._default = default
        return

    def decode(self, token):
        """ Convert a string token to a string.

        Surrounding whitespace and quotes are removed, and if the resulting
        string is null the default field value is used.

        """
        return token.strip().strip(self._quote) or self._default

    def encode(self, value):
        """ Convert a string to a string token.

        If the value is None the default field value is used (None is encoded 
        as a null string). For fixed-width fields the token is padded on the
        left or trimmed on the right to fit the allotted width.

        """
        value = value or self._default or ""
        token = self._valfmt(value)
        return token[:self.width].rjust(self.width) if self._fixed else token


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
        """ Convert a string token to a datetime.

	    If the token is an empty string the default field value is used.        

        """
        token = token.strip()
        if not token:
            return self._default
        return datetime.strptime(token, self._fmtstr)

    def encode(self, value):
        """ Convert a datetime to a string token.

        If the value is None the default field value is used (None is encoded 
        as a null string). For fixed-width fields the token is padded on the
        left or trimmed on the right to fit the allotted width.

        """
        value = value or self._default
        token = "" if value is None else self._fmtobj(value)
        if token and self._prec > 0:
            time, usecs = token.split(".")
            token = "{0:s}.{1:s}".format(time, usecs[0:self._prec])
        return token[:self.width].rjust(self.width) if self._fixed else token


class ListField(object):
    """ An array of composite field elements.

    """
    # An ListField is mapped to 0 or more input/output tokens.
    
    def __init__(self, name, pos, fields, default=None):
        """ Initialize this object.

        """
        self.name = name
        self.pos = slice(*pos)
        try:
            self.width = self.pos.stop - self.pos.start
        except TypeError:  # pos.stop is None
            self.width = None  # variable-width field
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
        return values

    def encode(self, values):
        """ Convert a sequence of Python values to a list of string tokens.

        If the value is None or an empty sequence the default field value is
        used (None is encoded as an empty list). Each element of the array 
        should be a dict-like object that corresponds to the field definitions 
        for this array.

        """
        values = values or self._default or []
        return [field.encode(elem.get(field.name)) for elem, field in
                product(values, self._fields)]


class ArrayField(ListField):
    """ Alias for ListField to maintain backwards compatibility.
    
    """
    def __init__(self, name, pos, fields, default=None):
        """ Initialize this object.

        """
        super(ArrayField, self).__init__(name, pos, fields, default)
        message = "ArrayField has been renamed to ListField"
        warn(message, DeprecationWarning)
        return

                
class RecordField(ListField):
    """ A composite field. 

    A RecordField is equivalent to the first element of an ListField with
    exactly one element, e.g. array_field[0]. 

    """
    # From an implementation perspective a RecordField *is* an ListField, but
    # semantically inheritance is a little murkier. For now, convenience
    # prevails.
        
    def __init__(self, name, pos, fields, default=None):
        """ Initialize this object.

        """
        if default is None:
            default = dict((field.name, field.decode("")) for field in fields)
        super(RecordField, self).__init__(name, pos, fields, [default])
        return

    def decode(self, tokens):
        """ Convert a sequence of string of tokens to a dict.

        This works for sequences of strings (e.g. from DelimitedReader) or a 
        string as a sequence (e.g. from FixedWidthReader). Each dict element
        corresponds to a component of this field.
        
        """
        return super(RecordField, self).decode(tokens)[0]

    def encode(self, value):
        """ Convert a Python dict to a list of string tokens.

        If the value is None or an empty dict the default field value is used
        (None is encoded as an empty list). 

        """
        values = [value] if value else self._default
        return super(RecordField, self).encode(values)
