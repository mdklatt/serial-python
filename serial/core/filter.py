""" Predefined filters.

"""
__all__ = ("BlacklistFilter", "WhitelistFilter")


class BlacklistFilter(object):
    """ Filter object to reject only certain records.
    
    """
    def __init__(self, field, values):
        """ Initialize this object.
        
        Reject all records where the value of 'field' is in 'values'.
        
        """
        self._field = field
        self._values = set(values)
        return
        
    def __call__(self, record):
        """ Implement the filter.
        
        """
        return record if record[self._field] not in self._values else None
        
    
class WhitelistFilter(object):
    """ Filter object to accept only certain records.
    
    """
    def __init__(self, field, values):
        """ Initialize this object.
        
        Reject all records where the value of 'field' is not in 'values'.

        """
        self._field = field
        self._values = set(values)
        return
        
    def __call__(self, record):
        """ Implement the filter.
        
        """
        return record if record[self._field] in self._values else None
