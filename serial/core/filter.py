""" Predefined filters.

"""
from __future__ import absolute_import

from re import compile


__all__ = ("FieldFilter", "RangeFilter", "RegexFilter", "SliceFilter")


class FieldFilter(object):
    """ Filter records by a specific field.
    
    This is intended for use with a Reader or Writer via their filter() method.
    
    """
    def __init__(self, field, values, blacklist=False):
        """ Initialize this object.
        
        By default, records that match one of the given field values are passed
        through and all other records are dropped (whitelisting). If blacklist 
        is True this is reversed (blacklisting).
        
        """
        self._field = field
        self._values = set(values)
        self._blacklist = blacklist
        return
        
    def __call__(self, record):
        """ Execute the filter.
        
        """
        try:
            match = record[self._field] in self._values
        except KeyError:  # no such field
            # The record is invalid for whitelisting because it doesn't have
            # the required field value; for blacklisting it's valid because it
            # doesn't have a prohibited field value.
            match = False
        return record if match != self._blacklist else None


class RangeFilter(object):
    """ Filter records by a range.
    
    This is intended for use with a Reader or Writer via their filter() method.
    
    """
    def __init__(self, field, min=None, max=None, blacklist=False):
        """ Initialize this object.
        
        By default, records whose 'field' value is within the range [min, max)
        are passed through and all other records are dropped (whitelisting). If
        blacklist is True this is reversed (blacklisting). If 'min' or 'max'
        is None that end of the range is considered to be unlimited. If both
        are None, the filter will pass all records if blacklist is True and
        drop all records if it's False.
                
        """
        self._field = field
        self._min = min
        self._max = max
        self._blacklist = blacklist
        return
        
    def __call__(self, record):
        """ Execute the filter.
        
        """
        value = record[self._field]
        match = ((self._min is None or self._min <= value) and
                 (self._max is None or value < self._max))
        return record if match != self._blacklist else None


class RegexFilter(object):
    """ Filter lines using a regular expression.
    
    This is intended for use with a FilteredIStream or FilteredOStream.
    
    """
    def __init__(self, regex, blacklist=False):
        """ Initialize this object.
        
        By default, lines that match the regular expression are passed through
        and all other lines are dropped (whitelisting). If blacklist is True 
        this is reversed (blacklisting).
        
        """
        self._regex = compile(regex)
        self._blacklist = blacklist
        return
        
    def __call__(self, line):
        """ Execute the filter.
        
        """
        match = self._regex.search(line) is not None
        return line if match != self._blacklist else None


class SliceFilter(object):
    """ Filter lines by slice.
    
    This is intended for use with a FilteredIStream or FilteredOStream.
    
    """
    def __init__(self, expr, values, blacklist=False):
        """ Initialize this object.
        
        The slice expression can be a pair of numbers or a slice object. By
        default, lines where the slice matches one of the values are passed
        through and all other lines are dropped (whitelisting). If blacklist
        is True this is reversed (blacklisting).
        
        """
        try:
            # Create a slice from a [beg, end) pair.
            self._slice = slice(*expr)
        except TypeError:  # not a sequence
            self._slice = expr
        self._values = set(values)
        self._blacklist = blacklist
        return
        
    def __call__(self, line):
        """ Execute the filter.
        
        """
        match = line[self._slice] in self._values
        return line if match != self._blacklist else None
