""" Predefined filters.

"""
from re import compile


__all__ = ("BoolFilter", "FieldFilter", "RangeFilter",
           "RegexFilter", "SliceFilter")


class _RecordFilter(object):
    """ Abstract base class for record filters.
    
    Record filters are intended for use with a Reader or Writer via their
    filter() method.
    
    """
    def __init__(self, field, blacklist=False):
        """ Initialize this object.
        
        By default, records that match on the value for the given field are 
        passed through and all other records are dropped (whitelisting). If 
        blacklist is True this is reversed (blacklisting).
        
        """
        self._field = field
        self._blacklist = blacklist
        return
        
    def __call__(self, record):
        """ Execute the filter.
        
        """
        try:
            match = self._match(record[self._field])
        except KeyError:
            match = False
        return record if match != self._blacklist else None
        
    def _match(self, value):
        """ Return True if the given field value is a match for the filter.
        
        Matching records will be passed along for whitelisting and dropped for
        blacklisting.
        
        """
        raise NotImplementedError
    

class BoolFilter(_RecordFilter):
    """ Filter records by the boolean value of a specific field.

    Accept values that are not false-y (False, 0, None, empty string, etc.) for
    whitelisting and reject them for blacklisting.

    """
    def __init__(self, field, blacklist=False):
        """ Initialize this object.

        """
        super(BoolFilter, self).__init__(field, blacklist)
        return

    def _match(self, value):
        """ Return True if the value is not false-y,

        """
        return bool(value)


class FieldFilter(_RecordFilter):
    """ Filter records by the value of a specific field.
    
    """
    def __init__(self, field, values, blacklist=False):
        """ Initialize this object.
                
        """
        super(FieldFilter, self).__init__(field, blacklist)
        self._values = set(values)
        return

    def _match(self, value):
        """ Return True if the value matches the set of filter values.
        
        """
        return value in self._values


class RangeFilter(_RecordFilter):
    """ Filter records based on a range of values.
    
    """
    def __init__(self, field, start=None, stop=None, blacklist=False):
        """ Initialize this object.
        
        Records are matched against the range [start, stop). If start or stop 
        is None that end of the range is considered to be unlimited.
        
        """
        super(RangeFilter, self).__init__(field, blacklist)
        self._start = start
        self._stop = stop
        return
        
    def _match(self, value):
        """ Return True if the value is within the filter range.
        
        """
        return ((self._start is None or self._start <= value) and
                (self._stop is None or value < self._stop))


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
