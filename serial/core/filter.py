""" Predefined filters.

"""
from __future__ import absolute_import

__all__ = ("BlacklistFilter", "WhitelistFilter")


class BlacklistFilter(object):
    """ Filter to reject specific records.
   
    This is intended for use with a Reader or Writer; see the filter() method.
     
    """
    def __init__(self, field, reject):
        """ Initialize this object.
        
        Reject all records 'field' value is in 'reject'.
        
        """
        self._field = field
        self._reject = set(reject)
        return
        
    def __call__(self, record):
        """ Implement the filter.
        
        """
        return None if record[self._field] in self._reject else record
        
    
class WhitelistFilter(object):
    """ Filter to accept specifc records.
    
    This is intended for use with a Reader or Writer; see the filter() method.
 
    """
    def __init__(self, field, accept):
        """ Initialize this object.
        
        Reject all records whose 'field' value is not in 'accept'.

        """
        self._field = field
        self._accept = set(accept)
        return
        
    def __call__(self, record):
        """ Implement the filter.
        
        """
        return record if record[self._field] in self._accept else None
 