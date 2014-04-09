""" Sorted input and output.

"""
from __future__ import absolute_import

from operator import itemgetter

from .buffer import _ReaderBuffer
from .buffer import _WriterBuffer


__all__ = ("SortReader", "SortWriter")


class _Sort(object):
    """ Base class for SortReader and SortWriter.
    
    """
    def __init__(self, key):
        """ Initialize this object.
        
        The key argument is either a single field name, a sequence of names,
        or a key function that returns a key value.
                        
        """
        if not callable(key):
            key = itemgetter(key)
        self._keyfunc = key
        self._buffer = []
        self._output = None  # defined by _ReaderBuffer or _WriterBuffer
        return
        
    def _queue(self, record):
        """ Process each incoming record.
        
        """
        self._buffer.append(record)
        return
        
    def _flush(self):
        """ Send sorted records to the output queue.
        
        """
        self._buffer.sort(key=self._keyfunc)
        self._output = self._buffer
        self._buffer = None
        return


class SortReader(_Sort, _ReaderBuffer):
    """ Sort input from another reader.
    
    No input is available until all records have been read from the source
    reader.
    
    """
    def __init__(self, reader, key):
        """ Initialize this object.
        
        """
        _Sort.__init__(self, key)
        _ReaderBuffer.__init__(self, reader)
        return

    def _uflow(self):
        """ Handle an underflow condition.
        
        This is called when the input reader is exhausted and there are no
        records in the output queue.
        
        """
        if not self._buffer:
            # All data has been output.
            raise StopIteration
        self._flush()
        return
        

class SortWriter(_Sort, _WriterBuffer):
    """ Sort output for another writer.
    
    No output is available until close() is called for this writer.
    
    """
    def __init__(self, writer, key):
        """ Initialize this object.
        
        """
        _Sort.__init__(self, key)
        _WriterBuffer.__init__(self, writer)
        return
