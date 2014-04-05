""" Apply aggregate functions to data.

"""
from __future__ import absolute_import

from operator import itemgetter

from .buffer import _ReaderBuffer
from .buffer import _WriterBuffer


__all__ = ("AggregateReader", "AggregateWriter")


class _Aggregate(object):
    """ Base class for AggregateReader and AggregateWriter.
    
    During aggregation, incoming records are grouped, reduction functions are
    applied to each group, and a single record is output for each group.
    Records are presumed to be sorted such that all records in a group are 
    contiguous.
    
    """
    @classmethod
    def reduction(cls, callback, field, alias=None):
        """ Create a reduction function from a callback.
        
        The callback should take a sequence of values as its argument and
        return a value, e.g. the built-in function sum(). The field argument
        specifies which values to pass to the callback from the sequence of
        records being reduced. This is either a single name or sequence of
        names. In the latter case, arguments are passed to the callback as a
        sequence of tuples. By default the reduction field is named after the
        input field, or specify an alias.
        
        """
        def wrapper(records):
            """ Execute the callback as a reduction function.
            
            """
            return {alias: callback(map(get, records))}
            
        if not alias:
            alias = field
        if isinstance(field, basestring):
            field = field,
        get = itemgetter(*field)
        return wrapper
            
    def __init__(self, key):
        """ Initialize this object.
        
        The key argument is either a single field name, a sequence of names,
        or a key function. A key function must return a dict-like object
        specifying the name and value for each key field. Key functions are 
        free to create key fields that are not in the incoming data. 
        
        Because the key function is called for every record, optimization is 
        (probably) worthwile. For multiple key fields, passing in a hard-coded 
        key function instead of relying on the automatically-generated function 
        may be give better performance, e.g. 
            
            lambda record: {"key1": record["key1"], ...}
                
        """
        if not callable(key):
            if isinstance(key, basestring):
                # Define a single-value key function.
                name = key  # force static binding
                key = lambda record: {name: record[name]}
            else:
                # Define a key function for multiple fields.
                names = key  # force static binding
                key = lambda record: dict((key, record[key]) for key in names)
        self._keyfunc = key
        self._keyval = None
        self._buffer = []
        self._reductions = []        
        return

    def reduce(self, *callbacks):
        """ Add reductions to this object or clear all reductions (default).
        
        A reduction is an callable object that takes a sequence of records and
        aggregates them into a single dict-like result keyed by field name.
        A reduction can return one or more fields. Reduction fields do not have
        to match the incoming records. A reduction function is free to create
        new fields, and, conversely, incoming fields that do not have a
        reduction will not be in the aggregated data. The reduction() class
        method can be used to generate reduction functions from basic functions
        like sum() or max().
        
        Reductions are applied in order to each group of records in the input
        sequence, and the results are merged to create one record per group.
        If multiple reductions return a field with the same name, the latter
        value will overwrite the existing value.

        """
        if not callbacks:
            self._reductions = []
            return
        for callback in callbacks:
            self._reductions.append(callback)
        return
        
    def _queue(self, record):
        """ Process an incoming record.
        
        """
        keyval = self._keyfunc(record)
        if keyval != self._keyval:
            # This is a new group, finalize the buffered group.
            self._flush()
        self._buffer.append(record)
        self._keyval = keyval
        return

    def _flush(self):
        """ Apply all reductions to the buffered data and flush to output.
        
        """
        if not self._buffer:
            return
        record = self._keyval
        for callback in self._reductions:
            # If multiple callbacks return the same field values, the latter
            # value will overwrite the existing value.
            record.update(callback(self._buffer))
        self._output.append(record)
        self._buffer = []
        return
                

class AggregateReader(_Aggregate, _ReaderBuffer):
    """ Apply aggregate functions to input from another reader.
    
    """
    def __init__(self, reader, key):
        """ Initialize this object.
        
        """
        _Aggregate.__init__(self, key)
        _ReaderBuffer.__init__(self, reader)
        return

    def _uflow(self):
        """ Handle an underflow condition.
        
        This is called when the input reader is exhausted and there are no
        records in the output queue.
        
        """
        # Last chance to flush buffered data.
        if not self._buffer:
            # All data has been output.
            raise StopIteration
        self._flush()
        return


class AggregateWriter(_Aggregate, _WriterBuffer):
    """ Apply aggregate functions to output for another writer.
    
    """
    def __init__(self, writer, key):
        """ Initialize this object.
        
        """
        _Aggregate.__init__(self, key)
        _WriterBuffer.__init__(self, writer)
        return
