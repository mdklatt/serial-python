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
        aggregates them into a single dict-like result. Reductions are applied
        in order to each sequence of grouped records and merged into a single
        record for each group. This record will also contain the key fields.
        Using reductions, it's possible to remove existing fields in the 
        incoming data and create new fields.
        
        The reduction() function can be used to generate reductions from
        primitive functions like the sum() built-in.
        
        """
        if not callbacks:
            self._reductions = []
        else:
            self._reductions.extend(callbacks)
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
