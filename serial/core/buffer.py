""" Buffer types.

Buffers sit between client code and a reader or writer and do additional post-
or preprocessing, respectively. They are similar to filters except that they
are designed to operate on groups of records. Buffers are used as wrappers
around of a reader or writer (or another buffer), while filters act more like 
decorators.

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
        while not self._output and self._reader:
            # Keep pulling input from the reader until a record is available
            # for output or the reader is exhausted.
            try:
                record = self._reader.next()
            except StopIteration:  # _reader is exhausted
                # There may still be some records in the buffer so swallow the
                # exception for now.
                self._reader = None
                self._flush()
                break
            self._read(record)
        try:
            return self._output.pop(0)
        except IndexError:  # _output is empty
            # The reader is empty and _flush() has already been called so it's
            # time to stop.
            raise StopIteration
            
    def __iter__(self):
        """ Return an iterator for this object.

        """
        return self

    def _read(self, record):
        """ Do something with this record.
        
        The derived class must implement this method to add records to the 
        output queue as input records are processed.
        
        """
        raise NotImplementedError
        
    def _flush(self):
        """ Complete any buffering operations.
        
        This is called once as soon as the input reader is exhausted, so the 
        derived class has one last chance to do something before iteration is 
        halted. If there are any remaining records in the buffer they should be
        queued in _output.
        
        """
        return
