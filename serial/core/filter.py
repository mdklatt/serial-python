""" Predefined filters.

"""
from __future__ import absolute_import

from re import compile

__all__ = ("FieldFilter", "RegexFilter", "SliceFilter")


class FieldFilter(object):
    """ Filter records by a specific field.
    
    This is intended for use with a Reader or Writer via their filter() method.
    
    """
    def __init__(self, field, values, whitelist=True):
        """ Initialize this object.
        
        By default, records that match one of the given field values are passed
        through and all other records are dropped (whitelisting). If whitelist
        is False this is reversed (blacklisting).
        
        """
        self._field = field
        self._values = set(values)
        self._whitelist = whitelist
        return
        
    def __call__(self, record):
        """ Execute the filter.
        
        """
        try:
            valid = (record[self._field] in self._values) == self._whitelist
        except KeyError:  # no such field
            # The record is invalid for whitelisting because it doesn't have
            # the required field value; for blacklisting it's valid because it
            # doesn't have a prohibited field value.
            valid = not self._whitelist
        return record if valid else None


class RegexFilter(object):
    """ Filter lines using a regular expression.
    
    This is intended for use with a FilteredIStream or FilteredOStream.
    
    """
    def __init__(self, regex, whitelist=True):
        """ Initialize this object.
        
        By default, lines that match the regular expression are passed through
        and all other lines are dropped (whitelisting). If whitelist is False
        this is reversed (blacklisting).
        
        """
        self._regex = compile(regex)
        self._whitelist = whitelist
        return
        
    def __call__(self, line):
        """ Execute the filter.
        
        """
        valid = (self._regex.search(line) is not None) == self._whitelist
        return line if valid else None


class SliceFilter(object):
    """ Filter lines by slice.
    
    This is intended for use with a FilteredIStream or FilteredOStream.
    
    """
    def __init__(self, expr, values, whitelist=True):
        """ Initialize this object.
        
        The slice expression can be a pair of numbers or a slice object. By
        default, lines where the slice matches one of the values are passed
        through and all other lines are dropped (whitelisting). If whitelist
        is False this is reversed (blacklisting).
        
        """
        try:
            # Create a slice from a [beg, end) pair.
            self._slice = slice(*expr)
        except TypeError:  # not a sequence
            self._slice = expr
        self._values = set(values)
        self._whitelist = whitelist
        return
        
    def __call__(self, line):
        """ Execute the filter.
        
        """
        valid = (line[self._slice] in self._values) == self._whitelist
        return line if valid else None
