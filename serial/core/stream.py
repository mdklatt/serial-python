""" Tools for working with streams.

"""
from __future__ import absolute_import

from glob import iglob
from itertools import chain
from zlib import decompressobj
from zlib import MAX_WBITS

__all__ = ("IStreamBuffer", "IStreamZlib", "IFileSequence")


class _IStreamAdaptor(object):
    """ Abstract base class for an input stream adaptor.

    An adaptor can be used to make an input stream compatible with the Reader
    stream protocol, i.e. implementing a next() method that returns a single
    line of text from the stream.

    """
    def next(self):
        """ Return the next line of text from a stream.

        """
        raise NotImplementedError

    def __iter__(self):
        """ Return an iterator for this stream.

        """
        # Any object that implements a next() method is a Python iterator.
        return self


class _OStreamAdaptor(object):
    """ Abstract base class for an output stream adaptor.

    An adaptor can be used to make an output stream compatible with the Writer
    stream protocol, i.e. implementing a write() method that writes a single
    line of text to the stream.

    """
    def write(self):
        """ Write a line of text to the stream.

        """
        raise NotImplementedError


class IStreamBuffer(_IStreamAdaptor):
    """ Add buffering to an input stream.

    An IStreamBuffer buffers input from another stream so that it can support
    rewind() operations.

    """
    def __init__(self, stream, bufsize=1):
        """ Initialize this object.

        The input stream is any object that implements next() to retrieve a
        single line of text.

        """
        super(IStreamBuffer, self).__init__()
        self._stream = stream
        self._buffer = []  # newest record at end
        while len(self._buffer) < bufsize:
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

        If the stream has been rewound this will return the first saved record,
        otherwise the next record from the input stream.

        """
        try:
            line = self._buffer[self._bufpos]
            self._bufpos += 1
        except IndexError:
            # At the end of the buffer so get a new line.
            line = self._stream.next() 
            del self._buffer[0]
            self._buffer.append(line)
        return line

    def rewind(self, count=None):
        """ Rewind the buffer.
        
        By default rewind to the beginning of the buffer.

        """
        self._bufpos = 0 if count is None else max(0, self._bufpos - count)
        return


class IStreamZlib(_IStreamAdaptor):
    """ Add zlib decompression to an input stream.
    
    This adaptor can be used with any zlib-compressed data, including gzip
    files. Unlike the Python gzip module, this will work with network files 
    e.g. a urlopen() stream.
    
    """  
    # Adjust the block size to trade performance against memory usage. 
    block_size = 32*1024  # bytes; must be at least 4 bytes.
      
    def __init__(self, stream):
        """ Initialize this object.
        
        The input stream must implement a read() method that returns a user-
        specified number of bytes, c.f. a Python file object.
        
        """
        super(IStreamZlib, self).__init__()
        self._stream = stream
        self._zlib = decompressobj(MAX_WBITS + 32)  # auto zlib/gzip detect
        self._buffer = []
        return
            
    def next(self):
        """ Return the next line of text.
        
        """
        while True:
            # Find the end of the next complete line.
            try:
                pos = self._buffer.index("\n") + 1  # include newline in line
            except ValueError:  # index failed
                # Keep going as long as the stream is still good, otherwise
                # this is the last line (the newline is missing).
                if self._read():
                    continue
                pos = len(self._buffer) 
            break
        if not self._buffer:
            raise StopIteration
        line = "".join(self._buffer[:pos])
        self._buffer = self._buffer[pos:]
        return line
        
    def _read(self):
        """ Retrieve decompressed data from the stream.
        
        """
        # The block size is based on the compressed data; the returned data
        # size may be different.
        data = self._zlib.decompress(self._stream.read(self.block_size))
        self._buffer.extend(list(data))
        return len(data) > 0
        
        
class IFileSequence(_IStreamAdaptor):
    """ Combine a sequence of files into a input single stream.
    
    """    
    def __init__(self, *paths, **kwargs):
        """ Initialize this object.
        
        If keyword argument glob is True each path expression is globbed. This 
        will have the side effect of supressing errors for nonexistent files.
        
        """
        # Globbing will supress IOErrors for nonexistent files because iglob()
        # silently returns an empty sequence for non-matching expressions.
        super(IFileSequence, self).__init__()
        glob = kwargs.get("glob")
        self._paths = paths if not glob else chain(*map(iglob, paths))
        self._lines = iter(self)
        return;
    
    def next(self):
        """ Return the next line from the input file(s).
        
        """
        return self._lines.next()
                
    def __iter__(self):
        """ Iterate over every line in the input file(s).
        
        """
        for path in self._paths:
            with open(path, "r") as stream:
                for line in stream:
                    yield line
        return
