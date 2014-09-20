""" Sorted input and output.

"""
from __future__ import absolute_import

from collections import deque
from operator import itemgetter

from .buffer import _ReaderBuffer
from .buffer import _WriterBuffer


__all__ = ("SortReader", "SortWriter")


class _Sorter(object):
    """ Abstract base class for SortReader and SortWriter.
    
    """
    def __init__(self, key, group=None):
        """ Initialize this object.
        
        The key argument determines sort order and is either a single field 
        name, a sequence of names, or a key function that returns a key value.
        
        The optional group argument is like the key argument but is used to 
        group records that are already partially sorted. Records will be sorted 
        within each group rather than as a single sequence. If the groups are 
        small relative to the total sequence length this can significantly 
        improve performance and memory usage.
                        
        """
        def keyfunc(key):
            """ Create a key function. """
            if not key or callable(key):
                return key
            if isinstance(key, basestring):
                key = (key,)
            return itemgetter(*key)
            
        self._get_key = keyfunc(key)
        self._get_group = keyfunc(group)
        self._group = None
        self._buffer = []
        self._output = None  # initialized by derived classes
        return
        
    def _queue(self, record):
        """ Process each incoming record.
        
        """
        if self._get_group:
            group = self._get_group(record)
            if group != self._group:
                # This is a new group; process the previous group.
                self._flush()
            self._group = group
        self._buffer.append(record)
        return
        
    def _flush(self):
        """ Send sorted records to the output queue.
        
        """
        if not self._buffer:
            return
        self._buffer.sort(key=self._get_key)
        self._output = deque(self._buffer)
        self._buffer = []
        return


class SortReader(_Sorter, _ReaderBuffer):
    """ Sort input from another reader.
    
    """
    def __init__(self, reader, key, group=None):
        """ Initialize this object.
        
        """
        _Sorter.__init__(self, key, group)
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
        

class SortWriter(_Sorter, _WriterBuffer):
    """ Sort output for another writer.
    
    """
    def __init__(self, writer, key, group=None):
        """ Initialize this object.
        
        """
        _Sorter.__init__(self, key, group)
        _WriterBuffer.__init__(self, writer)
        return
