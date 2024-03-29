""" Writer types.

Writers convert data records to lines of text.

"""
from contextlib import contextmanager
from itertools import chain


__all__ = "DelimitedWriter", "FixedWidthWriter"


class _Writer:
    """ Abstract base class for all serial data writers.

    Serial data consists of sequential records. A _Writer provides an interface
    interface for writing serial data and allows for preprocessing of the data
    using filters.

    """
    def __init__(self):
        """ Initialize this object.

        The output stream is any object that implements write() to write a line
        of text.

        """
        # Class filters are always applied after any user filters. Derived 
        # classes can use these to do any final data manipulation before the
        # record is written to the stream.
        self._user_filters = []
        self._class_filters = []
        return

    def filter(self, *callbacks):
        """ Add filters to this writer or clear all filters (default).

        Filters are applied in order to each record before it is finally
        written. A filter is a callable object that accepts a data record as
        its only argument. Based on this record the filter can perform the 
        following actions:
        1. Return None to reject the record (it will not be written).
        2. Return the data record as is.
        3. Return a *new record.
        
        *Take care not to modify a mutable argument unless the caller doesn't
         expect write() to be free of side effects.

        """
        # This does not affect class filters.
        if not callbacks:
            self._user_filters = []
        else:
            self._user_filters.extend(callbacks)
        return

    def write(self, record):
        """ Write a record while applying filters.
        
        """
        for callback in chain(self._user_filters, self._class_filters):
            record = callback(record)
            if record is None:
                return
        self._put(record)
        return

    def dump(self, records):
        """ Write all records while applying filters.
        
        """
        for record in records:
            self.write(record)
        return

    def _put(self, record):
        """ Put a formatted record into the output stream.
        
        This is called after the record has been passed through all filters.
        
        """
        raise NotImplementedError


class _TabularWriter(_Writer):
    """ Abstract base class for tabular data writers.

    Tabular data is organized fields such that each field occupies the same
    position in each record. One line of text corresponds to a one complete
    record.

    """
    @classmethod
    @contextmanager
    def open(cls, stream, *args, **kwargs):
        """ Create a runtime context for a _TabularWriter and its stream.
        
        The arguments are passed to the writer's constructor, except that the
        first argument is either an open stream or a file path that is used to 
        open a text file for writing. In both cases the stream will be closed
        upon exit from the context block.
        
        """
        # This assumes that first argument for all derived class constructors
        # is the stream; if not, this will need to be overridden.
        try:
            stream = open(stream, "wt")
        except TypeError:  # not a valid path argument
            pass  # assume this is already an open stream
        yield cls(stream, *args, **kwargs)
        try:
            stream.close()
        except AttributeError:  # no close() method
            pass
        return
        
    def __init__(self, stream, fields, endl="\n"):
        """ Initialize this object.

        """
        super(_TabularWriter, self).__init__()
        self._stream = stream
        self._fields = tuple(fields)
        self._endl = endl
        return

    def _put(self, record):
        """ Put a formatted record into the output stream.
        
        This is called after the record has been passed through all filters.
        
        """
        tokens = []
        for field in self._fields:
            # Convert each field into a string token.
            token = field.encode(record.get(field.name))
            if isinstance(token, str):
                tokens.append(token)
            else:
                # A sequence of tokens (e.g. an ArrayType); expand inline.
                tokens.extend(token)
        self._stream.write(self._join(tokens) + self._endl)
        return

    def _join(self, tokens):
        """ Join a sequence of tokens into a line of text.

        """
        raise NotImplementedError


class DelimitedWriter(_TabularWriter):
    """ A writer for tabular data consisting of character-delimited fields.

    The position of each scalar field is be given as an integer index, and the
    position of an array field is a [beg, end) slice expression where the end
    is None for a variable-length array.

    """
    def __init__(self, stream, fields, delim, esc=None, endl="\n"):
        """ Initialize this object.

        To make the output compatible with a DataReader, any non-significant
        delimiters need to be escaped. Use the esc argument to specify an
        escape value if necessary.
                
        """
        super(DelimitedWriter, self).__init__(stream, fields, endl)
        self._delim = delim
        if esc:
            self._escape = lambda tokens: (token.replace(delim, esc+delim) for 
                                           token in tokens)
        else:
            self._escape = lambda tokens: tokens
        return

    def _join(self, tokens):
        """ A writer for tabular data consisting of fixed-width fields.

        The position of each field is given as [beg, end) slice expression 
        where the end is None for a variable-length array.

        """
        return self._delim.join(self._escape(tokens))


class FixedWidthWriter(_TabularWriter):
    """ A writer for fields delineated by character position.

    The position of each field is given as [beg, end) slice expression where
    the end is None for a variable-length array.

    """
    def _join(self, tokens):
        """ Join a sequence of tokens into a line of text.
        
        """
        # In this implementation the positions in self.fields don't matter;
        # tokens must be in he correct order, and each token must be the
        # correct width for that field.             
        return "".join(tokens)
