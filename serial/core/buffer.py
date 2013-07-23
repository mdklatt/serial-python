""" Classes for buffering input and output records.

Unlike filters, buffers can operate on muliple records simulataneously. Thus,
a buffer split one record into multiple records, merge multiple records into
one record, reorder records, or any combination thereof. Buffers can also do
basic filtering.

"""
from __future__ import absolute_import

from . reader import _Reader
from . writer import _Writer


class _ReaderBuffer(_Reader):
    """ Abstract base class for all reader buffers.
    
    A _ReaderBuffer applies postprocessing to records from another _Reader. The
    base class implements the Python iterator protocol for reading records
    from the buffer.
    
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
        while not self._output:
            # Keep pulling input from the reader until a record is available
            # for output or the reader is exhausted.
            try:
                self._queue(self._reader.next())
            except (AttributeError, StopIteration): 
                # Reader is exhausted so call _uflow() to get additional 
                # records.
                self._reader = None
                self._uflow()
                break
        try:
            return self._output.pop(0)
        except IndexError:  # _output is empty
            # The reader is empty and _uflow() has already been called so it's
            # time to stop.
            raise StopIteration 
            
    def _queue(self, record):
        """ Process this record.
        
        The derived class must implement this method to add records to the 
        output queue as records are read from _reader.
        
        """
        raise NotImplementedError
        
    def _uflow(self):
        """ Input is empty, feed output records from the buffer.
        
        This is called if the input reader has been exhausted. The derived
        class can use this to queue additional records in _output. Once _output 
        is empty iteration will stop.
        
        """
        return
        

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
        should be called in correct order, outermost buffer first.
        
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
