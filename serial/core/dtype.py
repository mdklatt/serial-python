""" Data types.

Data types are responsible for converting text tokens to/from Python values.

"""
import collections
import datetime
import itertools


__all__ = ("ConstType", "IntType", "FloatType", "StringType", "DatetimeType",
           "ArrayType")


class DataType(object):
    """ Base class for all data types.
    
    """
    def __init__(self, dtype, fmt, null):
        """ Initialize this object.
        
        The dtype argument is the Python data type for this type, fmt is a 
        Python format string (e.g. '>10s'), and null is used for missing
        input/output fields. For fixed-width fields fmt *must* specify the
        field width.
        
        """
        self._dtype = dtype
        self._fmt = fmt
        self._null = null
        return
        
    def decode(self, token):
        """ Convert a text token to a Python value.
        
        """
        try:
            value = self._dtype(token.strip())
        except ValueError:  # type conversion failed
            value = self._null
        return value
    
    def encode(self, value):
        """ Convert a Python value to a text token. 
        
        """
        if value is None:
            value = self._null
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
    def __init__(self, fmt="d", null=None):
        """ Initialize this object.
        
        """
        super(IntType, self).__init__(int, fmt, null)
        return


class FloatType(DataType):
    """ A floating point value.
    
    """
    def __init__(self, fmt="f", null=None):
        """ Initialize this object.
        
        """
        super(FloatType, self).__init__(float, fmt, null)
        return
    
    
class StringType(DataType):
    """ A string value.
    
    """
    def __init__(self, fmt="s", quote="", null=None):
        """ Initialize this object.
        
        """
        super(StringType, self).__init__(str, fmt, null)
        self._quote = quote
        return

    def decode(self, token):
        """ Convert a text token to a string.
        
        """
        value = token.strip().strip(self._quote)
        if not value:
            value = self._null
        return value
    
    def encode(self, value):
        """ Convert a string to a text token. 
        
        """
        if value is None:
            value = self._null
        return "{0:s}{1:s}{0:s}".format(self._quote, format(value, self._fmt))
        
                
class DatetimeType(DataType):
    """ A datetime value.
    
    """
    def __init__(self, timefmt, null=None):
        """ Initialize this object.
        
        """
        super(DatetimeType, self).__init__(datetime.datetime, "{:s}", null)
        self._timefmt = timefmt
        return
        
    def decode(self, token):
        """ Convert a text token to a datetime.
        
        """
        token = token.strip()
        if not token:
            value = self._null
        else:
            value = datetime.datetime.strptime(token, self._timefmt)
        return value
        
    def encode(self, value):
        """ Convert a datetime to a text token.
        
        """
        try:
            token = value.strftime(self._timefmt)
        except AttributeError:
            token = self._null.strftime(self._timefmt)
        return token
    
    
class ArrayType(DataType):
    """ An array of DataTypes. 
    
    """
    def __init__(self, fields, null=list()):
        """ Initialize this object.
        
        """
        super(ArrayType, self).__init__(list, "{:s}", null)
        Field = collections.namedtuple("Field", ("name", "pos", "dtype"))
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
        values = []
        for pos in range(0, len(tokens), self._elem_width):
            elem = tokens[pos:pos+self._elem_width]
            values.append({field.name: field.dtype.decode(elem[field.pos]) for
                           field in self._fields})
        return values
        
    def encode(self, values):
        """ Convert an array of values to a sequence of text tokens.
        
        """
        return [field.dtype.encode(elem.get(field.name)) for elem, field in
                itertools.product(values, self._fields)]
            
        
        