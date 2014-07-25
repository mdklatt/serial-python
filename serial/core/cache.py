""" Cached input and output.

"""
from __future__ import absolute_import

from .buffer import _ReaderBuffer


__all__ = ("CacheReader",)


class CacheReader(_ReaderBuffer):
    """ Cache reader input to allow for rewinding.
    
    """
    def __init__(self, reader, maxlen=None):
        """ Initialize this object.
        
        By default, all input is cached, or specify maxlen to limit the 
        number of records.
        
        """
        # Using a plain list as the buffer because random access approaches
        # O(n) for a deque.
        super(CacheReader, self).__init__(reader)
        self._maxlen = maxlen
        self._buffer = []
        self._bufpos = 0  
        return
        
    def rewind(self, count=None):
        """ Rewind the reader.
        
        Rewind to the first saved record by default, or specify a count.
        
        """
        self._bufpos = 0 if count is None else max(0, self._bufpos - count)
        return
                
    def _queue(self, record):
        """ Process each incoming record.
        
        """
        if len(self._buffer) == self._maxlen:
            # Remove a record to maintain the buffer at maxlen
            self._buffer.pop(0)
        self._buffer.append(record)
        self._bufpos += 1
        self._output.append(record)
        return
        
    def _uflow(self):
        """ Send a record to the output queue.
        
        """
        try:
            self._output.append(self._buffer[self._bufpos])
        except IndexError:  # at end of buffer
            raise StopIteration
        self._bufpos += 1
        return
