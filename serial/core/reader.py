""" Reader types.

Readers convert lines of text to data records.

"""
from ._util import make_fields

__all__ = ("DelimitedReader", "FixedWidthReader")


class SerialReader(object):
    """ Abstract base class for all serial data readers.

    Serial data consists of sequential records. A SerialReader provides an
    iterator interface for reading serial data and allows for precprocessing of
    the data using filters.

    """
    def __init__(self):
        """ Initialize this object.
        
        """
        self._filters = []
        return

    def filter(self, callback=None):
        """ Add a filter to this reader or clear all filters (default).

        A filter is a callable object that accepts a data record as its only
        argument. Based on this record the filter can perform the following
        actions:
        1. Return None to reject the record (the iterator will drop it).
        2. Return the data record as is.
        3. Return a *new record.
        4. Raise StopIteration to signal the end of input.
        
        *Input filters can safely modify their argument.
        
        """
        if callback is None:
            self._filters = []
        else:
            self._filters.append(callback)
        return
        
    def next(self):
        """ Return the next filtered record.
        
        This implements the Python iterator protocol.
        
        """
        record = None
        while record is None:
            # Repeat until a record passes all filters.
            record = self._get()
            for callback in self._filters:
                # Apply each filter in order. Stop as soon as the record fails
                # a filter and try the next record.
                record = callback(record)
                if record is None:
                    break
        return record
        
    def __iter__(self):
        """ Iterate over all filtered input records.
        
        """
        # Anything that implements next() is a Python iterator.
        return self
            
    def _get(self):
        """ Get the next parsed record from the input source.
        
        This is the last step before any filters get applied to the record and
        its returned to the client. The implementation *must* raise a
        StopIteration exception to signal that input has been exhausted.
            
        """
        raise NotImplementedError
        
        

class TabularReader(SerialReader):
    """ Abstract base class for tabular data readers.

    Tabular data is organized into fields such that each field occupies the 
    same position in each input record. One line of text corresponds to a one 
    complete record.

    """
    def __init__(self, stream, fields):
        """ Initialize this object.

        The stream can be any object that implements a readline() method.

        """
        super(TabularReader, self).__init__()
        self._stream = stream
        self._buffer = []
        self._fields = make_fields(fields)
        return

    def _get(self):
        """ Return the next record from the stream.

        This function implements the Pyhthon iterator idiom and raises a
        StopIterator exception when the input stream is exhausted.

        """
        line = self._getline()
        return {field.name: field.dtype.decode(token) for (field, token)
                in zip(self._fields, self._parse(line.rstrip()))}

    def _parse(self, line):
        """ Parse a line of text into a sequence of tokens.

        """
        raise NotImplementedError

    def _getline(self):
        """ Get the next line from the stream.

        """
        try:
            line = self._buffer.pop(0)
        except IndexError:  # _buffer is empty
            line = self._stream.readline()
        if not line:
            raise StopIteration
        return line

    def _putback(self, line):
        """ Place a line into the read buffer.

        This is useful, for example, for parsing file headers where the only
        way to know the header is complete is by encountering the first line of
        data. The data line can then be put back into the read buffer and read
        as normal.

        """
        self._buffer.append(line)
        return line


class DelimitedReader(TabularReader):
    """ A reader for delimited lines of text.

    The position of each scalar field is be given as an integer index, and the
    position of an array field is the pair [beg, end).

    """
    def __init__(self, stream, fields, delim=None):
        """ Initialize this object.

        The default delimiter will parse lines delimited by any whitespace. At
        this time there is no way to escape delimiters.

        """
        super(DelimitedReader, self).__init__(stream, fields)
        self._delim = delim
        return

    def _parse(self, line):
        """ Parse each line of input into a sequence of tokens.

        Lines are split at each occurrence of the delimiter; the delimiter is
        discarded.

        """
        tokens = line.split(self._delim)
        return [tokens[field.pos] for field in self._fields]


class FixedWidthReader(TabularReader):
    """ A reader for lines of text delineated by character position.

    The character position of each field is given as the pair [beg, end).

    """
    def _parse(self, line):
        """ Parse each line of input into a sequence of tokens.

        Lines are split based on the specified position of each field.

        """
        return [line[field.pos] for field in self._fields]


# class ContextualReader(Reader):
#     """ A reader for contextual lines.
#
#     Fields are determined by context rather than position, and all lines do not
#     necessarily have the same fields.
#
#     """
#     def _scan(line):
#         """ Scan a line of input.
#
#         """
#         # Return a dict of tokens keyed by the field name.
#         pass


