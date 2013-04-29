""" Tools for working with streams.

"""
__all__ = ("IStreamAdaptor", "IStreamBuffer", "OStreamAdaptor")


class IStreamAdaptor:
    """ Abstract base class for an input stream adaptor.

    An adaptor can be used to make an input source compatible with the Reader
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


class IStreamBuffer(IStreamAdaptor):
    """ Add buffering to a stream.

    An IStreamBuffer buffers input from another stream so that it can support
    rewind() operations.

    """
    def __init__(self, stream, bufsize=1):
        """ Initialize this object.

        The input stream is any object that implements next() to retrieve a
        single line of text.

        """
        self._stream = stream
        self._buffer = []
        while len(self._buffer) < bufsize:
            # Fill the buffer one record at a time.
            try:
                self._buffer.append(self._stream.next())
            except StopIteration:  # stream is exhausted
                # Wait until the buffer is exhausted to raise an exception.
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
            # At the end of the buffer, so get a new line.
            line = self._stream.next()
            del self._buffer[0]
        return line

    def rewind(self, count=1):
        """ Rewind the stream buffer.

        """
        self._bufpos = max(0, self._bufpos - abs(count))
        return


class OStreamAdaptor(object):
    """ Abstract base class for an output stream adaptor.

    An adaptor can be used to make an output source compatible with the Writer
    stream protocol, i.e. implementing a write() method that writes a single
    line of text to the stream.

    """
    def write(self):
        """ Write a line of text to the stream.

        """
        raise NotImplementedError
