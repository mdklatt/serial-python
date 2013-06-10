""" Private utility functions.

"""
from collections import namedtuple


Field = namedtuple("Field", ("name", "pos", "dtype", "width"))

def field_type(name, pos, dtype):
    """ Create a Field tuple.
    
    """
    try:
        pos = slice(*pos)
        width = pos.stop - pos.start
    except TypeError:  # pos is an int
        width = 1
    return Field(name, pos, dtype, width)    


def strftime(time, timefmt):
    """ Return a datetime-like object as a formatted string. 
    
    This is a replacement for datetime.strftime that handles years before 1900.    
    Only the most basic fields are supported, and it is not locale-aware.
    
    """
    datetime = []
    pos = 0
    while pos < len(timefmt):
        char = timefmt[pos]
        if char == strftime._esc:
            pos += 1
            try:
                fmt, get = strftime._fields[timefmt[pos]]
            except KeyError:
                raise ValueError("unknown strftime field: {0:s}".format(s))
            except IndexError:
                raise ValueError("timefmt cannot end with escape character")
            char = format(get(time), fmt)
        datetime.append(char)
        pos += 1
    return "".join(datetime)

# Iniitialize these values once instead of with every function call.

strftime._esc = "%"
strftime._fields = {
    strftime._esc: ("s", lambda time: strftime._esc),
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
