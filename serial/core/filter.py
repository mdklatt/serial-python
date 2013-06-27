""" Predefined filters.

"""
from __future__ import absolute_import

__all__ = ("BlacklistFilter", "WhitelistFilter")


class BlacklistFilter(object):
    """ Filter object to reject only certain records.
    
    """
    def __init__(self, field, reject):
        """ Initialize this object.
        
        Reject all records where the value of 'field' is in 'reject'.
        
        """
        self._field = field
        self._reject = set(reject)
        return
        
    def __call__(self, record):
        """ Implement the filter.
        
        """
        return record if record[self._field] not in self._reject else None
        
    
class WhitelistFilter(object):
    """ Filter object to accept only certain records.
    
    """
    def __init__(self, field, accept):
        """ Initialize this object.
        
        Reject all records where the value of 'field' is not in 'accept'.

        """
        self._field = field
        self._accept = set(accept)
        return
        
    def __call__(self, record):
        """ Implement the filter.
        
        """
        return record if record[self._field] in self._accept else None
