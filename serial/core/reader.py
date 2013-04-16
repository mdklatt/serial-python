""" Reader types.

Readers convert lines of text to data records.

"""
from ._util import make_fields

__all__ = ("DelimitedReader", "FixedWidthReader")


class SerialReader(object):
    """ Base class for all serial data readers.

    Serial data consists of individual records stored as lines of text.

    """
    def __init__(self, stream):
        self._stream = stream
        self._buffer = []
        return

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


class TabularReader(SerialReader):
    """ Abstract base class for tabular data readers.

    Tabular data is organized fields such that each field occupies the same
    position in each record. One line of text corresponds to a one complete
    record.

    """
    def __init__(self, stream, fields):
        """ Initialize this object.

        The stream can be any object that implements a readline() method.

        """
        super(TabularReader, self).__init__(stream)
        self._fields = make_fields(fields)
        self._filters = []
        return

    def filter(self, func=None):
        """ Add a filter to this object or clear all filters.

        A filter is a function that accecpts a data record as its argument.
        The function returns to True to accept the records or False to reject
        it (it will be not passed to the user). Because the record is a dict,
        the function can also modify it in place. Records are passed through
        filters in the order the were added.

        Calling the function with no arguments will clear all filters.

        """
        if func is None:
            self._filters = []
        else:
            self._filters.append(func)
        return

    def next(self):
        """ Return the next record from the stream.

        This function implements the Pyhthon iterator idiom and raises a
        StopIterator exception when the input stream is exhausted.

        """
        record = None
        while record is None:
            line = self._getline()
            record = {field.name: field.dtype.decode(token) for (field, token)
                      in zip(self._fields, self._parse(line.rstrip()))}
            for func in self._filters:
                if not func(record):
                    record = None
                    break
        return record

    def __iter__(self):
        """ Iterate over all records in the stream.

        """
        return self

    def _parse(self, line):
        """ Parse a line of text into a sequence of tokens.

        """
        raise NotImplementedError


class DelimitedReader(TabularReader):
    """ A reader for delimited lines of text.

    The position of each scalar field is be given as an integer index, and the
    position of an array field is the pair [beg, end).

    """
    def __init__(self, source, fields, delim=None):
        """ Initialize this object.

        The default delimiter will parse lines delimited by any whitespace. At
        this time there is no way to escape delimiters.

        """
        super(DelimitedReader, self).__init__(source, fields)
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
    """ A reader for fields delineated by character position.

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


