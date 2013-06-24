""" Internal utility clases and functions for the serial.core package.

"""
from __future__ import absolute_import

class Field(object):
    """ A serial data field.
    
    """
    def __init__(self, name, pos, dtype):
        """ Initialize this object.
        
        """
        try:
            pos = slice(*pos)
        except TypeError:  # pos is an int
            width = 1
        else:
            try:
                width = pos.stop - pos.start
            except TypeError:  # stop is None
                # Variable-length field; acutual width must be determined
                # during encoding or decoding.
                width = None
        self.pos = pos
        self.name = name
        self.dtype = dtype
        self.width = width
        return


class TimeFormat(object):
    """ Convert datetime-like objects to formatted strings. 
    
    This is a replacement for datetime.strftime that handles years before 1900.    
    Only the most basic fields are supported, and it is not locale-aware.
    
    """
    _escape = "%"
    _field_defs = {
        "d": ("02d", lambda time: time.day),
        "f": ("06d", lambda time: time.microsecond),
        "H": ("02d", lambda time: time.hour),
        "I": ("02d", lambda time: time.hour%12),
        "M": ("02d", lambda time: time.minute),
        "m": ("02d", lambda time: time.month),
        "p": ("s", lambda time: "AM" if t.hour < 12 else "PM"),  # no locale
        "S": ("02d", lambda time: time.second),
        "Y": ("04d", lambda time: time.year),
        "y": ("02d", lambda time: time.year%100)}

    @staticmethod
    def _scan(timefmt):
        """ Iterate over the timefmt string while unescaping characters.

        The return values are a (char, esc) pair where esc is True if char was
        preceded by the escape character.

        """
        esc = False
        for char in timefmt:
            if char == TimeFormat._escape and not esc:
                # This is an escape character that has not itself been escaped.
                esc = True
            else:
                # A regular character.
                yield char, esc
                esc = False
        return
    
    def __init__(self, timefmt):
        """ Initialize this object.
        
        """
        # The presumed use case is multiple conversions using the same format
        # string, so scan the string once and build a template.
        self._template = []
        self._fields = []
        for char, esc in self._scan(timefmt):
            if not esc:
                # A character literal
                self._template.append(char)
                continue
            # Add a new field.
            try:
                field = self._field_defs[char]
            except:
                raise ValueError("uknown field specifier: {0:s}".format(char))
            self._template.append("{{{0:d}:s}}".format(len(self._fields)))
            self._fields.append(field)
        self._template = "".join(self._template)
        return

    def __call__(self, time):
        """ Convert a datetime to a string.
        
        """
        tokens = [format(func(time), fmt) for fmt, func in self._fields]
        return self._template.format(*tokens)