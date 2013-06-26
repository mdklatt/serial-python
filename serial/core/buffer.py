""" Buffer types.

Buffers sit between client code and a reader or writer and do additional post-
or preprocessing, respectively. They are similar to filters except that they
are designed to operate on groups of records. Buffers are used as wrappers
around a reader or writer (or another buffer), while filters act more like 
decorators.

"""
from __future__ import absolute_import

from . reader import _Reader


class _ReaderBuffer(_Reader):
    """ Abstract base class for all reader buffers.
    
    The Python iterator protocol is implemented for retrieving records from the
    buffer.
    
    """
    def __init__(self, reader):
        """ Initialize this object.
        
        The input reader can be a _Reader or another _ReaderBuffer.
        
        """
        super(_ReaderBuffer, self).__init__()
        self._reader = reader
        self._output = []  # FIFO
        return
        
    def _get(self):
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
            self._queue(record)
        try:
            return self._output.pop(0)
        except IndexError:  # _output is empty
            # The reader is empty and _flush() has already been called so it's
            # time to stop.
            raise StopIteration
            
    def _queue(self, record):
        """ Process this record.
        
        The derived class must implement this method to add records to the 
        output queue as records are read from _reader.
        
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
        

class _WriterBuffer(object):
    """ Abstract base class for all writer buffers.
    
    Records are written to the buffer using the write() or dump() methods.
    
    """
    def __init__(self, writer):
        """ Initialize this object.
        
        The writer can be a _Writer or another _WriterBuffer.
        
        """
        self._writer = writer
        self._output = []  # FIFO
        return
        
    def write(self, record):
        """ Write this record to the buffer.
        
        """
        # Process this record, then write any new records in the output queue
        # to the destination writer.
        self._queue(record)
        while self._output:
            self._writer.write(self._output.pop(0))
        return
        
    def dump(self, records):
        """ Write all records to the destination writer.
        
        This automatically calls close().
        
        """
        for record in records:
            self.write(record)
        self.close()
        return

    def close(self):
        """ Close the buffer.
        
        All remaining records in the buffer will be written to the destination
        writer, and no further writes should be done to the buffer. This does 
        not close the destination writer itself.
        
        """
        self._flush()
        for record in self._output:
            self._writer.write(record)
        self._output = None
        self._writer = None
        return

    def _queue(self, record):
        """ Process this record.
        
        The derived class must implement this method to add records to the 
        output queue as records are written to the buffer.
        
        """
        raise NotImplementedError

    def _flush(self):
        """ Complete any buffering operations.
        
        This is called as soon as close() is called, so the derived class has
        one last chance to do something. There will be no more records to
        process, so any remaining records in the buffer should be queued in
        _output.
        
        """
        return