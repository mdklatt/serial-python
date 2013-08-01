""" Classes for buffering input and output records.

Unlike filters, buffers can operate on muliple records simulataneously. Thus,
a buffer can split one record into multiple records, merge multiple records 
into one record, reorder records, or any combination thereof. 

"""
from __future__ import absolute_import

from . reader import _Reader
from . writer import _Writer


class _ReaderBuffer(_Reader):
    """ Abstract base class for all reader buffers.
    
    A _ReaderBuffer applies postprocessing to records from another _Reader. The
    base class implements the iterator protocol for reading records from the
    buffer.
    
    """
    def __init__(self, reader):
        """ Initialize this object.
        
        The input reader can be any _Reader, including another _ReaderBuffer.
        
        """
        super(_ReaderBuffer, self).__init__()
        self._reader = reader
        self._output = []  # FIFO
        return
        
    def _get(self):
        """ Return the next buffered input record.
        
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
        """ Process each incoming record.

        This is called for each record that is read from the input reader and 
        must be implemented by derived classes.
        
        """
        raise NotImplementedError
        
    def _uflow(self):
        """ Handle an underflow condition.
        
        This is called to retrieve additional records if the output queue is 
        empty and the input reader has been exhausted. Derived classes can 
        override this as necessary. 
        
        """
        # Derived classes must raise StopIteration to signal the end of input.
        raise StopIteration
        

class _WriterBuffer(_Writer):
    """ Abstract base class for all writer buffers.
    
    The base class implements write() and dump() for writing records to the
    buffer.
    
    """
    def __init__(self, writer):
        """ Initialize this object.
        
        The writer can be a _Writer or another _WriterBuffer.
        
        """
        super(_WriterBuffer, self).__init__()
        self._writer = writer
        self._output = []  # FIFO
        return
        
    def dump(self, records):
        """ Write all records to the destination writer.
        
        This automatically calls close().
        
        """
        super(_WriterBuffer, self).dump(records)
        self.close()
        return

    def close(self):
        """ Close the buffer.
        
        All remaining records in the buffer will be written to the destination
        writer, and no further writes should be done to the buffer. This does 
        not close the destination writer itself.
        
        If multiple _WriterBuffers are being chained, their close() methods
        should be called in the correct order (outermost buffer first).
        
        """
        self._flush()
        for record in self._output:
            # Base class write() applies filters.
            super(_WriterBuffer, self).write(record) 
        self._output = None
        self._writer = None
        return

    def write(self, record):
        """ Write this record to the buffer.
        
        """
        # Process this record, then write any new records in the output queue
        # to the destination writer.
        self._queue(record)
        for record in self._output:
            # Base class write() applies filters.
            super(_WriterBuffer, self).write(record) 
        self._output = []
        return
        
    def _put(self, record):
        """ Write this record to the destination writer.
        
        """
        # At this point the record has already been buffered and filtered.
        self._writer.write(record)
        return

    def _queue(self, record):
        """ Process this record.
        
        This is called for each record that is written to the buffer and must 
        be implemented by derived classes.
        
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
