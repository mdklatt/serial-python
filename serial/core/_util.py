""" Private utility functions.

"""
import collections


def make_fields(fields):
    """ Convert (name, pos, dtype) sequences to Fields
    
    """
    Field = collections.namedtuple("Field", ("name", "pos", "dtype"))
    arr = []
    for name, pos, dtype in fields:
        try:
            pos = slice(*pos)
        except TypeError:  # pos is an int
            pass
        arr.append(Field(name, pos, dtype))
    return arr


def strftime(time, timefmt):
    """ Return a datetime-like object as a formatted string. 
    
    This is a replacement for datetime.strftime that handles years before 1900.    
    Only the most basic fields are supported, and it is not locale-aware.
    
    """
    datetime = []
    pos = 0
    while pos < len(timefmt):
        s = timefmt[pos]
        if s == strftime._esc:
            pos += 1
            try:
                fmt, get = strftime._fields[timefmt[pos]]
            except KeyError:
                raise ValueError("unknown strftime field: {0:s}".format(s))
            except IndexError:
                raise ValueError("timefmt cannot end with escape character")
            s = format(get(time), fmt)
        datetime.append(s)
        pos += 1
    return "".join(datetime)

# Iniitialize these values once instead of with every function call.

strftime._esc = "%"
strftime._fields = {
    strftime._esc: ("s", lambda t: strftime._esc),
    "d": ("02d", lambda t: t.day),
    "f": ("06d", lambda t: t.microsecond),
    "H": ("02d", lambda t: t.hour),
    "I": ("02d", lambda t: t.hour%12),
    "M": ("02d", lambda t: t.minute),
    "m": ("02d", lambda t: t.month),
    "p": ("s", lambda t: "AM" if t.hour < 12 else "PM"),  # no locale
    "S": ("02d", lambda t: t.second),
    "Y": ("04d", lambda t: t.year),
    "y": ("02d", lambda t: t.year%100)}
