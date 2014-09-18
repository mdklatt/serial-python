""" Sorted input and output.

"""
from __future__ import absolute_import

from collections import deque
from operator import itemgetter

from .buffer import _ReaderBuffer
from .buffer import _WriterBuffer


__all__ = ("SortReader", "SortWriter")


class _Sort(object):
    """ Base class for SortReader and SortWriter.
    
    """
    def __init__(self, key, group=None):
        """ Initialize this object.
        
        The key argument determines sort order and is either a single field 
        name, a sequence of names, or a key function that returns a key value.
        
        The optional group argument is like the key argument but is used to 
        group records that are already partially sorted. Records will be sorted 
        within each group rather than as a single sequence. This reduces memory 
        usage, but the effect on performance is mixed. If the groups are small 
        relative to the total sequence length, grouping increases performance. 
        However, as group size increases the performance advantage decreases 
        and eventually goes negative.
                        
        """
        self._keyfunc = key if callable(key) else itemgetter(key)
        if group:
            group = group if callable(group) else itemgetter(group)
        self._groupfunc = group
        self._groupval = None
        self._buffer = []
        self._output = None  # defined by _ReaderBuffer or _WriterBuffer
        return
        
    def _queue(self, record):
        """ Process each incoming record.
        
        """
        if self._groupfunc:
            groupval = self._groupfunc(record)
            if groupval != self._groupval:
                # This is a new group; process the previous group.
                self._flush()
            self._groupval = groupval
        self._buffer.append(record)
        return
        
    def _flush(self):
        """ Send sorted records to the output queue.
        
        """
        if not self._buffer:
            return
        self._buffer.sort(key=self._keyfunc)
        self._output = deque(self._buffer)
        self._buffer = []
        return


class SortReader(_Sort, _ReaderBuffer):
    """ Sort input from another reader.
    
    No input is available until all records have been read from the source
    reader.
    
    """
    def __init__(self, reader, key, group=None):
        """ Initialize this object.
        
        """
        _Sort.__init__(self, key, group)
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
    def __init__(self, writer, key, group=None):
        """ Initialize this object.
        
        """
        _Sort.__init__(self, key, group)
        _WriterBuffer.__init__(self, writer)
        return
