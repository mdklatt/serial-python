""" Internal utility clases for the serial.core package.

"""
from __future__ import absolute_import


class TimeFormat(object):
    """ Convert datetime-like objects to formatted strings. 
    
    This is a replacement for datetime.strftime that handles years before 1900.    
    Only the most basic fields are supported, and it is not locale-aware.
    
    """
    _escape = "%"
    _formats = {
        "d": ("02d", lambda time: time.day),
        "f": ("06d", lambda time: time.microsecond),
        "H": ("02d", lambda time: time.hour),
        "I": ("02d", lambda time: time.hour%12),
        "M": ("02d", lambda time: time.minute),
        "m": ("02d", lambda time: time.month),
        "p": ("s", lambda time: "AM" if time.hour < 12 else "PM"),  # no locale
        "S": ("02d", lambda time: time.second),
        "Y": ("04d", lambda time: time.year),
        "y": ("02d", lambda time: time.year%100)}

    def __init__(self, timefmt):
        """ Initialize this object.
        
        """
        def scan():
            """ Iterate over timefmt while unescaping characters. """
            esc = False
            for char in timefmt:
                if char == self._escape and not esc:
                    # An unescaped escape character.
                    esc = True
                else:
                    # A regular character.
                    yield char, esc
                    esc = False
            return

        # The presumed use case is multiple conversions using the same format
        # string, so scan the string once and build a template.
        self._template = []
        self._fields = []
        for char, esc in scan():
            if not esc:
                # A character literal
                self._template.append(char)
                continue
            # Add a new field.
            try:
                field = self._formats[char]
            except:
                raise ValueError("unknown field specifier: {0:s}".format(char))
            self._template.append("{{{0:d}:s}}".format(len(self._fields)))
            self._fields.append(field)
        self._template = "".join(self._template)
        return

    def __call__(self, time):
        """ Convert a datetime to a string.
        
        """
        tokens = [format(func(time), fmt) for fmt, func in self._fields]
        return self._template.format(*tokens)
