""" Buffer types.

Buffers sit between client code and a reader or writer and do additional post-
or preprocessing, repsectively. They are similar to filters except that they
are designed to operate on groups of records. For example, a buffer can merge
multiple records into a single record or expand a single record into multiple 
records. Also, buffers are used as interfaces on top of a reader or writer 
(or another buffer), while filters act more like decorators.

"""
__all__ = ()


class _ReaderBuffer(object):
    """ Abstract base class for all reader buffers.
    
    This implements the basic _Reader interface for iterating over records.
    
    """
    def __init__(self, reader):
        """ Initialize this object.
        
        The input reader can be a _Reader or another _ReaderBuffer.
        
        """
        self._reader = reader
        self._output = []  # FIFO
        return
        
    def next(self):
        """ Return the next buffered input record.
        
        """
        while not self._output:
            # Keep retrieving records from the reader until a new record is
            # available for output or input is exhausted.
            try:
                record = self._reader.next()
            except StopIteration:
                self._flush()
                if self._output:
                    break
                raise
            self._read(record)
        return self._output.pop(0)

    def __iter__(self):
        """ Return an iterator for this object.

        """
        return self  # see next()
            
    def _read(self, record):
        """ Do something with this record.
        
        """
        raise NotImplementedError
        
    def _flush(self):
        """ The reader is exhausted.
        
        The derived class has one last chance to do something before iteration
        is halted. If there are any remaining input records they should be 
        queued in _output.
        
        If additional records are placed in _output this will be called again, 
        so the derived class should be prepared for multiple invocations.
        
        """
        return
