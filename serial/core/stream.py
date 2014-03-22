""" Tools for working with streams.

"""
from __future__ import absolute_import

from collections import deque
from zlib import decompressobj
from zlib import MAX_WBITS

__all__ = ("BufferedIStream", "FilteredIStream", "FilteredOStream",
           "GzippedIStream")


class _StreamAdaptor(object):
    """ Abstract base class for a stream adaptor.
    
    """
    def __init__(self, stream):
        """ Initialize this object. 
        
        The adaptor assumes responsibility for closing the stream when the 
        adaptor's close() method is called or when exiting a context block.
        
        """
        self._stream = stream
        return
    
    def close(self):
        """ Close the adaptor and its stream.
        
        """
        try:
            self._stream.close()
        except AttributeError:  # no close()
            pass
        return
    
    
class _IStreamAdaptor(_StreamAdaptor):
    """ Abstract base class for an input stream adaptor.

    This can be used to make an input stream compatible with the Reader stream
    protocol.

    """
    def next(self):
        """ Return the next line of text from a stream.

        """
        raise NotImplementedError

    def __iter__(self):
        """ Return an iterator for this stream.

        """
        return self
        

class BufferedIStream(_IStreamAdaptor):
    """ Add buffering to an input stream.

    The buffered stream can be rewound to lines previously retrieved via the
    next() method.

    """
    def __init__(self, stream, buflen=1):
        """ Initialize this object.

        """
        super(BufferedIStream, self).__init__(stream)
        self._buffer = deque(maxlen=buflen) 
        while len(self._buffer) < buflen:
            # Fill the buffer one record at a time.
            try:
                self._buffer.append(self._stream.next())
            except StopIteration:  # stream is exhausted
                # Don't raise StopIteration until self.next() is called with an
                # exhausted buffer.
                break
        self._bufpos = 0  # always points to the current record
        return

    def next(self):
        """ Return the next line of text.

        If the stream has been rewound this will return the first buffered 
        line, otherwise the next line from the input stream.

        """
        try:
            line = self._buffer[self._bufpos]
            self._bufpos += 1
        except IndexError:
            # At the end of the buffer so get a new line.
            line = self._stream.next()
            self._buffer.append(line)  # pops _buffer[0]
        return line

    def rewind(self, count=None):
        """ Rewind the buffer.
        
        By default rewind to the beginning of the buffer.

        """
        self._bufpos = 0 if count is None else max(0, self._bufpos - count)
        return


class FilteredIStream(_IStreamAdaptor):
    """ Add filtering to an input stream.
    
    Stream filters are applied before the stream input is parsed by the Reader;
    this can be faster than using Reader filters. A filter is a callable object
    that accepts a line from the stream's next() method and performs one of the 
    following actions:
    1. Return None to reject the line (it will not be passed to the reader).
    2. Return the line as is.
    3. Return a new/modified line.
    4. Raise StopIteration to signal the end of input.
       
    """
    def __init__(self, stream):
        """ Initialize this object.
        
        """
        super(FilteredIStream, self).__init__(stream)
        self._filters = []
        return
    
    def filter(self, *callbacks):
        """ Add filters to this stream or clear all filters (default).
        
        """
        if not callbacks:
            self._filters = []
        else:
            self._filters.extend(callbacks)
        return
    
    def next(self):
        """ Return the next filtered line from the stream.
        
        """
        # Recursion would simplify this, but would fail for any combination of
        # filters that rejected more than 1000 consecutive lines (the Python
        # recursion limit).
        line = None
        while line is None:
            # Repeat until a line passes all filters.
            line = self._stream.next()
            for callback in self._filters:
                # Apply each filter in order. Stop as soon as the line fails
                # a filter.
                line = callback(line)
                if line is None:
                    break
        return line


class GzippedIStream(_IStreamAdaptor):
    """ Add gzip/zlib decompression to a text input stream.
    
    Unlike the Python gzip module, this will work with streaming data, e.g. a
    urlopen() stream.
    
    """
    read_size = 1024  # bytes; adjust to maximize performance
      
    def __init__(self, stream):
        """ Initialize this object.
        
        The input stream must implement a read() method that returns a user-
        specified number of bytes, e.g. any file-like object.
        
        """
        super(GzippedIStream, self).__init__(stream)
        self._decode = decompressobj(MAX_WBITS + 32).decompress
        self._buffer = ""
        return
            
    def next(self):
        """ Return the next line of text.
        
        """
        def read():
            """ Retrieve decompressed data from the stream. """
            # The block size is based on the compressed data; the returned data
            # size may be different. 
            data = self._stream.read(self.read_size)
            if not data:
                # Check for EOF before decoding because the decoded value will
                # be an empty string if data does not contain a complete
                # encoded sequence.
                return False
            self._buffer += self._decode(data)
            return True
        
        while True:
            # Find the end of the next complete line.
            try:
                pos = self._buffer.index("\n") + 1  # include \n
            except ValueError:  # \n not found
                # Keep going as long as the stream is still good, otherwise
                # this is the last line (the newline is missing).
                if read():
                    continue
                pos = len(self._buffer) 
            break
        if not self._buffer:
            raise StopIteration
        line = self._buffer[:pos]
        self._buffer = self._buffer[pos:]
        return line


class _OStreamAdaptor(_StreamAdaptor):
    """ Abstract base class for an output stream adaptor.

    This can be used to make an output stream compatible with the Writer stream 
    protocol.

    """
    def write(self, line):
        """ Write a line of text to the stream.

        """
        raise NotImplementedError


class FilteredOStream(_OStreamAdaptor):
    """ Add filtering to an output stream.
    
    Stream filters are applied to the text output after it has been generated 
    by the Writer. This can be used, for example, to apply low-level text
    formatting. A filter is a callable object that accepts a line of text and 
    performs one of the following actions:
    1. Return None to reject the line (it will not be written to the stream).
    2. Return the line as is.
    3. Return a new/modified line.
       
    """
    def __init__(self, stream):
        """ Initialize this object.
        
        """
        super(FilteredOStream, self).__init__(stream)
        self._filters = []
        return
    
    def filter(self, *callbacks):
        """ Add filters to this stream or clear all filters (default).
        
        """
        if not callbacks:
            self._filters = []
        else:
            self._filters.extend(callbacks)
        return

    def write(self, line):
        """ Write a filtered line to the stream.
        
        """
        for callback in self._filters:
            # Apply each filter to the line.
            line = callback(line)
            if line is None:
                return
        self._stream.write(line)
        return
