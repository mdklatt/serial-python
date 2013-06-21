""" Writer types.

Writers convert data records to lines of text.

"""
from . _util import Field

__all__ = ("DelimitedWriter", "FixedWidthWriter")


class _Writer(object):
    """ Abstract base class for all serial data writers.

    Serial data consists of individual records stored as lines of text.

    """
    def __init__(self):
        """ Initialize this object.

        The output stream is any object that implements write() to write a line
        of text.

        """
        self._filters = []
        return

    def filter(self, *callbacks):
        """ Add a filter to this writer or clear all filters.

        A filter is a callable object that accepts a data record as its only
        argument. Based on this record the filter can perform the following
        actions:
        1. Return None to reject the record (it will not be written).
        2. Return the data record as is.
        3. Return a new* record.
        
        *Take care not to modify a mutable argument unless the caller doesn't
         expect write() to be free of side effects.

        """
        if not callbacks:
            self._filters = []
        else:
            self._filters.extend(callbacks)
        return

    def write(self, record):
        """ Write a record to the output stream.
        
        """
        for callback in self._filters:
            record = callback(record)
            if record is None:
                return
        self._put(record)
        return

    def dump(self, records):
        """ Write all records to the output stream.
        
        """
        for record in records:
            self.write(record)
        return

    def _put(self, record):
        """ Write a record to the output stream.
        
        This is called after the record has been passed through all filters.
        
        """
        raise NotImplementedError


class _TabularWriter(_Writer):
    """ Abstract base class for tabular data writers.

    Tabular data is organized fields such that each field occupies the same
    position in each record. One line of text corresponds to a one complete
    record.

    """
    def __init__(self, stream, fields, endl="\n"):
        """ Initialize this object.

        """
        super(_TabularWriter, self).__init__()
        self._stream = stream
        self._fields = [Field(*args) for args in fields]
        self._endl = endl
        return

    def _put(self, record):
        """ Write a filtered record to the output stream.

        """
        tokens = []
        for index, field in enumerate(self._fields):
            token = field.dtype.encode(record.get(field.name))
            if isinstance(token, basestring):
                tokens.append(token)
            else:
                # A sequence of tokens (e.g. an ArrayType); expand inline and
                # update the field width and position based on the actual size
                # of the field.
                tokens.extend(token)
                end = field.pos.start + field.dtype.width
                field.pos = slice(field.pos.start, end)
                field.width = field.dtype.width
                self._fields[index] = field
        self._stream.write(self._join(tokens) + self._endl)
        return

    def _join(self, tokens):
        """ Join a sequence of tokens into a line of text.

        """
        raise NotImplementedError


class DelimitedWriter(_TabularWriter):
    """ A writer for fields delineated by a delimiter.

    The position of each scalar field is be given as an integer index, and the
    position of an array field is the pair [beg, end).

    """
    def __init__(self, stream, fields, delim, endl="\n"):
        """ Initialize this object.

        At this time there is no escaping of characters in the input records
        that match the delimiter; this may cause issues when trying to parse
        the resulting output.

        """
        super(DelimitedWriter, self).__init__(stream, fields, endl)
        self._delim = delim
        return

    def _join(self, tokens):
        """ Join a sequence of tokens into a line of text.

        """
        return self._delim.join(tokens)


class FixedWidthWriter(DelimitedWriter):
    """ A writer for fields delineated by character position.

    The character position of each field is given as the pair [beg, end).

    """
    # In this implementation the positions in self.fields don't matter; tokens
    # must be in he correct order, and each token must be the correct width for
    # that field. The _DataType format for a fixed-width field *MUST* have a
    # field width, e.g. '6.2f'.       
    def __init__(self, stream, field, endl="\n"):
        """ Initialize this object.
        
        """
        super(FixedWidthWriter, self).__init__(stream, field, "", endl)
        return
