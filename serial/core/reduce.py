""" Apply aggregate functions to data.

"""
from __future__ import absolute_import

from operator import itemgetter

from .buffer import _ReaderBuffer
from .buffer import _WriterBuffer


__all__ = ("reduction", "AggregateReader", "AggregateWriter")


def reduction(key, func):
    """ Decorate a function for use with an aggregator.
    
    The function should take a sequence of values and return a single result,
    e.g. the sum() built-in. The decorated function will operate on a single 
    field in a sequence of data records. 
    
    """
    return lambda records: {key: func(map(itemgetter(key), records))}


class _Aggregator(object):
    """ Base class for AggregateReader and AggregateWriter.
    
    An aggregator groups incoming records, applies reductions to the records in
    each group, and outputs a single record for each group. Records are
    presumed to be sorted such that all records in a group are contiguous.
    
    """
    def __init__(self, keyname, keyfunc=None):
        """ Initilize this object.
        
        The keyname is the field name or sequence of names that define the
        key fields for the grouped data. The keyfunc is used to calculate a key
        value for each record. It must return a tuple of values corresponding
        to each key field. Key fields do not have to be existing fields in the
        data; define keyname and keyfunc to give the desired key field values.
        
        The default keyfunc is an identity function for the given keyname
        fields. In this case, these fields must be in the incoming data.
        
        """
        if isinstance(keyname, basestring):
            keyname = (keyname,)
        if not keyfunc:
            keyfunc = lambda record: tuple(record[key] for key in keyname)
        self._keyname = tuple(keyname)
        self._keyfunc = keyfunc
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
        reduction will not be in the aggregated data.
        
        Reductions are applied in order to each group of records in the input
        sequence, and the results are merged to create one record per group.
        If multiple reductions return a field with the same name, the latter
        value will overwrite the existing value.
        
        A reduction can be specifed as a (field, func) pair instead of a
        callback. In this case, a reduction function will be generated that
        applies the function to the given field and returns a value with the
        same field name. This is intended for use with functions like sum(),
        max(), etc.
        
        """
        if not callbacks:
            self._reductions = []
            return
        for callback in callbacks:
            try:
                # Generate a reduction for the given field and function. 
                key, func = callback
                callback = self._make_reduction(key, func)
            except TypeError:
                # Not iterable, assume this is a callback.
                pass
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
        record = dict(zip(self._keyname, self._keyval))
        for callback in self._reductions:
            # If multiple callbacks return the same field values, the latter
            # value will overwrite the existing value.
            record.update(callback(self._buffer))
        self._output.append(record)
        self._buffer = []
        return
        
    @classmethod
    def _make_reduction(cls, name, func):
        """ Wrap a function for use with reduce().
    
        The function should take a sequence of values and return a single 
        result, e.g. the sum() built-in. The reusulting function will operate 
        on a single field in a sequence of data records. By default the 
        reduction field will have the same name as the input field, or specify
        a different value for 'field'.
    
        """
        def wrapper(records):
            """ Apply the function to the given field. """
            return {name: func(map(itemgetter(name), records))}
            
        return wrapper
        

class AggregateReader(_Aggregator, _ReaderBuffer):
    """ Apply aggregate functions to input from another reader.
    
    """
    def __init__(self, reader, keyname, keyfunc=None):
        """ Initilize this object.
        
        """
        _Aggregator.__init__(self, keyname, keyfunc)
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


class AggregateWriter(_Aggregator, _WriterBuffer):
    """ Apply aggregate functions to output for another writer.
    
    """
    def __init__(self, writer, keyname, keyfunc=None):
        """ Initilize this object.
        
        """
        _Aggregator.__init__(self, keyname, keyfunc)
        _WriterBuffer.__init__(self, writer)
        return
