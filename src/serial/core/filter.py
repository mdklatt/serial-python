""" Predefined filters.

"""
from re import compile
from typing import Optional


__all__ = ("BoolFilter", "CountFilter", "FieldFilter", "RangeFilter",
           "RegexFilter", "SliceFilter")


class CountFilter:
    """ Add a count field.

    This will count the number of records that pass through this filter, which
    may not be the same as the total number of records read or written due to
    the actions of other filters.

    Use this with a Reader or Writer via its filter() method.

    """
    def __init__(self, field: str, start=1):
        """ Initialize this object

        :param field: output field
        :param start: start value
        """
        self._field = field
        self._count = start
        return

    def __call__(self, record: dict) -> dict:
        """ Increment the count.

        :param record: input record
        :return: modified record
        """
        record[self._field] = self._count
        self._count += 1
        return record


class _MatchFilter:
    """ Abstract filter base class for matching records.
    
    """
    def __init__(self, field: str, blacklist=False):
        """ Initialize this object.
        
        By default, records that match on the value for the given field are 
        passed through and all other records are dropped (whitelisting).

        :param field: input field
        :param blacklist: True to blacklist matching records
        """
        self._field = field
        self._blacklist = blacklist
        return
        
    def __call__(self, record: dict) -> Optional[dict]:
        """ Match a record.

        Matching records will be passed along for whitelisting and dropped for
        blacklisting.

        :param record: input record
        :return: input record or None
        """
        try:
            match = self._match(record[self._field])
        except KeyError:
            match = False
        return record if match != self._blacklist else None
        
    def _match(self, value) -> bool:
        """ Return True if the given field value is a match for the filter.
        
        """
        raise NotImplementedError
    

class BoolFilter(_MatchFilter):
    """ Filter records by the boolean value of a specific field.

    Accept values that are not false-y (False, 0, None, empty string, etc.) for
    whitelisting and reject them for blacklisting.

    Use this with a Reader or Writer via its filter() method.

    """
    def __init__(self, field: str, blacklist=False):
        """ Initialize this object.

        :param field: input field
        :param blacklist: True to blacklist matching records
        """
        super(BoolFilter, self).__init__(field, blacklist)
        return

    def _match(self, value) -> bool:
        """ Convert the value to a bool.

        :return: True if the value is not false-y
        """
        return bool(value)


class FieldFilter(_MatchFilter):
    """ Filter records by the value of a specific field.

    Use this with a Reader or Writer via its filter() method.

    """
    def __init__(self, field: str, values, blacklist=False):
        """ Initialize this object.

        :param field: input field
        :param values: values to match
        :param blacklist: True to blacklist matching records
        """
        super(FieldFilter, self).__init__(field, blacklist)
        self._values = set(values)
        return

    def _match(self, value) -> bool:
        """ Match a value against the filter values.

        :return: True for matching vale
        """
        return value in self._values


class RangeFilter(_MatchFilter):
    """ Filter records based on a range of values.

    Use this with a Reader or Writer via its filter() method.

    """
    def __init__(self, field: str, start=None, stop=None, blacklist=False):
        """ Initialize this object.
        
        Records are matched against the range [start, stop). If start or stop 
        is None that end of the range is considered to be unlimited.

        :param field: input field
        :param start: range start (inclusive)
        :param stop: range stop (exclusive)
        :param blacklist: True to blacklist matching records
        """
        super(RangeFilter, self).__init__(field, blacklist)
        self._start = start
        self._stop = stop
        return
        
    def _match(self, value) -> bool:
        """ Match the record against the filter range.

        :return: True if the value is within the range
        """
        lower = self._start is None or self._start <= value
        upper = self._stop is None or value < self._stop
        return lower and upper


class RegexFilter:
    """ Filter lines using a regular expression.
    
    This is intended for use with a FilteredIStream or FilteredOStream.
    
    """
    def __init__(self, regex: str, blacklist=False):
        """ Initialize this object.
        
        By default, lines that match the regular expression are passed through
        and all other lines are dropped (whitelisting).

        :param regex: regular expression to match
        :param blacklist: True to blacklist matching records
        """
        self._regex = compile(regex)
        self._blacklist = blacklist
        return
        
    def __call__(self, line: str) -> Optional[str]:
        """ Match a line.

        :param line: input line
        :return: input line or None
        """
        match = self._regex.search(line) is not None
        return line if match != self._blacklist else None


class SliceFilter:
    """ Filter lines by slice.
    
    This is intended for use with a FilteredIStream or FilteredOStream.
    
    """
    def __init__(self, expr, values, blacklist=False):
        """ Initialize this object.
        
        The slice expression can be a pair of numbers or a slice object. By
        default, lines where the slice matches one of the values are passed
        through and all other lines are dropped (whitelisting).

        :param expr: slice expression
        :param values: values to match
        :param blacklist: True to blacklist matching records
        """
        try:
            # Create a slice from a [beg, end) pair.
            self._slice = slice(*expr)
        except TypeError:  # not a sequence
            self._slice = expr
        self._values = set(values)
        self._blacklist = blacklist
        return
        
    def __call__(self, line: str) -> Optional[str]:
        """ Match a line.

        :param line: input line
        :return: input line or None
        """
        match = line[self._slice] in self._values
        return line if match != self._blacklist else None
