""" Predefined filters.

"""
from __future__ import absolute_import

from re import compile

__all__ = ("FieldFilter",)


class FieldFilter(object):
    """ Filter records by a specific field.
    
    This is intended for use with a Reader or Writer via their filter() method.
    
    """
    def __init__(self, field, values, whitelist=True):
        """ Initialize this object.
        
        By default, records that match one of the given field values are passed
        through and all other records are dropped (whitelisting). If whitelist
        if False this is reversed (blacklisting).
        
        """
        self._field = field
        self._values = set(values)
        self._whitelist = whitelist
        return
        
    def __call__(self, record):
        """ Execute the filter.
        
        """
        valid = (record[self._field] in self._values) == self._whitelist
        return record if valid else None
