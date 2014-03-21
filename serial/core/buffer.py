""" Classes for buffering input and output records.

Unlike filters, buffers can operate on multiple records simultaneously. Thus,
a buffer can split one record into multiple records, merge multiple records 
into one record, reorder records, or any combination thereof. 

"""
from __future__ import absolute_import

from .reader import _Reader
from .writer import _Writer


class _ReaderBuffer(_Reader):
    """ Abstract base class for all Reader buffers.
    
    A _ReaderBuffer applies postprocessing to records being read from another 
    _Reader.
    
    """
    def __init__(self, reader):
        """ Initialize this object.
        
        """
        super(_ReaderBuffer, self).__init__()
        self._reader = reader
        self._output = []  # FIFO
        return
        
    def _get(self):
        """ Read the next buffered record from the input reader.
        
        This is called before any of this buffer's filters have been applied.
        
        """
        while not self._output:
            try:
                self._queue(self._reader.next())
            except (AttributeError, StopIteration):
                # Underflow condition.
                self._reader = None
                self._uflow()  # raises StopIteration on EOF
        return self._output.pop(0)
            
    def _queue(self, record):
        """ Process an incoming record.

        This is called for each record that is read from the input reader and 
        must be implemented by derived classes. A StopIteration exception can
        be raise to signal the end of input prior to an EOF condition.
        
        """
        raise NotImplementedError
        
    def _uflow(self):
        """ Handle an underflow condition.
        
        This is called to retrieve additional records if the output queue is 
        empty and the input reader has been exhausted. Derived classes can 
        override this as necessary. A StopIteration exception must be raised
        to signal that there are no more records in the buffer. 
        
        """
        raise StopIteration
        

class _WriterBuffer(_Writer):
    """ Abstract base class for all Writer buffers.
    
    A _WriterBuffer applies preprocessing to records being written to another
    _Writer.

    """
    def __init__(self, writer):
        """ Initialize this object.
        
        """
        super(_WriterBuffer, self).__init__()
        self._writer = writer
        self._output = []  # FIFO
        return
        
    def write(self, record):
        """ Write a record while applying buffering and filtering.
        
        """
        # Process this record, then write any new records in the output queue
        # to the destination writer.
        self._queue(record)
        for record in self._output:
            # Base class write() applies filters.
            super(_WriterBuffer, self).write(record) 
        self._output = []
        return

    def close(self):
        """ Close the buffer.
        
        This is a signal to flush any remaining records in the buffer to the
        output writer. No further writes should be done to this buffer. This
        does not close the destination writer itself.
        
        If multiple WriterBuffers are being chained, their close() methods
        should be called in the correct order (outermost buffer first).
        
        """
        if not self._writer:
            # Buffer is already closed.
            return
        self._flush()
        for record in self._output:
            # Base class write() applies filters.
            super(_WriterBuffer, self).write(record) 
        self._output = None
        self._writer = None
        return

    def dump(self, records):
        """ Write all records while applying buffering and filtering.
        
        This automatically calls close().
        
        """
        super(_WriterBuffer, self).dump(records)
        self.close()
        return
        
    def _put(self, record):
        """ Send a buffered record to the destination writer.
        
        This is called after the record has passed through all this buffer's
        filters.
        
        """
        self._writer.write(record)
        return

    def _queue(self, record):
        """ Process an incoming record.
        
        This is called for each record that is written to the buffer and must 
        be implemented by derived classes.
        
        """
        raise NotImplementedError

    def _flush(self):
        """ Complete any buffering operations.
        
        This is called as soon as close() is called, so the derived class has
        one last chance to do something. There will be no more records to
        process, so any remaining records in the buffer should be queued for
        output.
        
        """
        return
