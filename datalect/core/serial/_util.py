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
