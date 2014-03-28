""" Apply aggregate functions to data.

"""
from __future__ import absolute_import

from .buffer import _ReaderBuffer
from .buffer import _WriterBuffer


__all__ = ("AggregateReader", "AggregateWriter")


class _AggregateBuffer(object):
    """ Base class for AggregateReader and AggregateWriter
    
    """
    def __init__(self, keyname, keyfunc=None):
        """ Initilize this object.
        
        """
        if isinstance(keyname, basestring):
            keyname = (keyname,)
        if not keyfunc:
            keyfunc = lambda record: tuple(record[key] for key in keyname)
        self._keyname = keyname
        self._keyfunc = keyfunc
        self._keyval = None
        self._buffer = {}
        self._aggregates = []        
        return

    def apply(self, keyname, callback):
        """ Add an aggregate function for the given field(s)
        
        The keyname argument is either a single name or sequence of names that
        the callback will be applied to. The callback must accept one argument
        per name in keyname, in that same order. It must als return on result
        per name in keyname that order. The value(s) passed in to the callback 
        will a sequence of all the current values in the aggregate group for 
        the given field name. 
        
        """
        if isinstance(keyname, basestring):
            keyname = (keyname,)
        self._aggregates.append((keyname, callback))
        return
        
    def _queue(self, record):
        """ Process this record.
        
        """
        keyval = self._keyfunc(record)
        if keyval != self._keyval:
            self._flush()
        for key in record:
            self._buffer.setdefault(key, []).append(record[key])
        self._keyval = keyval
        return

    def _flush(self):
        """ Apply all aggregates to the buffered data and flush to output.
        
        """
        if not self._buffer:
            return
        record = dict(zip(self._keyname, self._keyval))
        for keyname, callback in self._aggregates:
            result = callback(*[self._buffer[key] for key in keyname])
            if len(keyname) == 1:
                record[keyname[0]] = result
            else:
                record.update(dict(zip(keyname, result)))
        self._output.append(record)
        self._buffer = {}
        return


class AggregateReader(_AggregateBuffer, _ReaderBuffer):
    """ Apply aggregate functions to input from another reader.
    
    """
    def __init__(self, reader, keyname, keyfunc=None):
        """ Initilize this object.
        
        """
        _AggregateBuffer.__init__(self, keyname, keyfunc)
        _ReaderBuffer.__init__(self, reader)
        return

    def _uflow(self):
        """ Finalize processing on EOF.
        
        """
        # There are no more incoming records, so flush any buffered data.
        if not self._buffer:
            raise StopIteration
        self._flush()
        return


class AggregateWriter(_AggregateBuffer, _WriterBuffer):
    """ Apply aggregate functions to output for another writer.
    
    """
    def __init__(self, writer, keyname, keyfunc=None):
        """ Initilize this object.
        
        """
        _AggregateBuffer.__init__(self, keyname, keyfunc)
        _WriterBuffer.__init__(self, writer)
        return
