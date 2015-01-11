""" Reader types.

Readers convert lines of text to data records.

"""
from __future__ import absolute_import

from collections import deque
from contextlib import contextmanager
from functools import partial
from itertools import chain
from re import compile

__all__ = "DelimitedReader", "FixedWidthReader", "ChainReader"


class _Reader(object):
    """ Abstract base class for all serial data readers.

    Serial data consists of sequential records. A _Reader provides an iterator
    interface for reading serial data and implements data filtering.

    """
    def __init__(self):
        """ Initialize this object.

        The input stream is any object that implements next() to return the
        next line of text input.

        """
        # Class filters are always applied before any user filters. Derived
        # classes can use these to do any preliminary data manipulation after
        # the record is parsed.
        self._class_filters = []
        self._user_filters = []
        return

    def filter(self, *callbacks):
        """ Add filters to this reader or clear all filters (default).

        Filters are applied in order to each record after is has been read. A 
        filter is a callable object that accepts a data record as its only 
        argument. Based on this record the filter can perform the following 
        actions:
        1. Return None to reject the record (the iterator will drop it).
        2. Return the data record as is.
        3. Return a *new record.
        4. Raise StopIteration to signal the end of input.

        *Input filters can safely modify a mutable argument.

        """
        # This does not affect class filters.
        if not callbacks:
            self._user_filters = []
        else:
            self._user_filters.extend(callbacks)
        return

    def next(self):
        """ Read the next record while applying filtering.

        """
        # Recursion would simplify this, but would fail for any combination of
        # filters that rejected more than 1000 consecutive records (the Python
        # recursion limit).
        record = None
        while record is None:
            # Repeat until a record passes all filters.
            record = self._get()
            for callback in chain(self._class_filters, self._user_filters):
                # Apply each filter in order. Stop as soon as the record fails
                # a filter and try the next record.
                record = callback(record)
                if record is None:
                    break
        return record

    def __iter__(self):
        """ Iterate over all records while applying filtering.

        """
        return self

    def _get(self):
        """ Get the next parsed record from the input stream.

        This is called before any filters have been applied. The implementation 
        must raise a StopIteration exception to signal when input has been 
        exhausted.

        """
        raise NotImplementedError


class _TabularReader(_Reader):
    """ Abstract base class for tabular data readers.

    Tabular data is organized into fields such that each field occupies the
    same position in each input record. One line of text corresponds to one
    complete record.

    """
    @classmethod
    @contextmanager
    def open(cls, stream, *args, **kwargs):
        """ Create a runtime context for a _TabularReader and its stream.
        
        The arguments are passed to the reader's constructor, except that the
        first argument is either an open stream or a path that is used to open
        a text file for reading. In both cases the stream will be closed upon
        exit from the context block.
        
        """
        # This assumes that first argument for all derived class constructors
        # is the stream; if not, this will need to be overridden.
        if isinstance(stream, basestring):
            # Treat this as a file path.
            stream = open(stream, "r")
        yield cls(stream, *args, **kwargs)
        try:
            stream.close()
        except AttributeError:  # no close()
            pass
        return
    
    def __init__(self, stream, fields, endl="\n"):
        """ Initialize this object.

        """
        super(_TabularReader, self).__init__()
        self._stream = stream
        self._fields = tuple(fields)
        self._endl = endl
        return

    def _get(self):
        """ Get the next parsed record from the input stream.

        This is called before any filters have been applied. A StopIteration 
        exception is raised on EOF.

        """
        tokens = self._split(self._stream.next().rstrip(self._endl))
        return dict((field.name, field.decode(token)) for (field, token) in
                    zip(self._fields, tokens))

    def _split(self, line):
        """ Split a line of text into a sequence of string tokens.

        """
        raise NotImplementedError


class DelimitedReader(_TabularReader):
    """ A reader for tabular data consisting of character-delimited fields.

    The position of each scalar field is be given as an integer index, and the
    position of an array field is a [beg, end) slice expression where the end
    is None for a variable-length array.

    """
    def __init__(self, stream, fields, delim=None, esc=None, endl="\n"):
        """ Initialize this object.

        The default delimiter will parse lines delimited by any whitespace.
        Delimiters can be escaped by defining the esc argument. Delimiters 
        immediately following the escape value are ignored during parsing.
        (There is currently no way to escape the escape value).

        """
        super(DelimitedReader, self).__init__(stream, fields, endl)
        if esc:
            # Regex patterns need to be encoded in case the escape character 
            # has a special meaning.
            patt = "{0:s}{1:s}".format(esc, delim).encode("string-escape")
            unescape = partial(compile(patt).sub, delim)
            patt = "(?<!{0:s}){1:s}".format(esc, delim).encode("string-escape")
            split = compile(patt).split
            self._tokenize = lambda line: [unescape(s) for s in split(line)]
        else:
            self._tokenize = lambda line: line.split(delim)
        return

    def _split(self, line):
        """ Split a line of text into a sequence of string tokens.

        Lines are split at each occurrence of the delimiter; the delimiter is
        discarded.

        """
        tokens = self._tokenize(line)
        return tuple(tokens[field.pos] for field in self._fields)


class FixedWidthReader(_TabularReader):
    """ A writer for tabular data consisting of fixed-width fields.

    The position of each field is given as [beg, end) slice expression where 
    the end is None for a variable-length array.

    """
    def _split(self, line):
        """ Split a line of text into a sequence of string tokens.

        Lines are split based on the string position of each field.

        """
        return tuple(line[field.pos] for field in self._fields)


class ChainReader(_Reader):
    """ Read a sequence of streams as a single series of records.
    
    The ChainReader opens streams as necessary and closes them once they
    have been read.
    
    """
    @classmethod
    @contextmanager
    def open(cls, streams, reader, *args, **kwargs):
        """ Create a runtime context for a ChainReader and its streams.
        
        The arguments are passed to the class constructor. Each stream is
        closed once it has been exhausted, and any open streams remaining in
        the sequence will be closed upon exit from the context block.
        
        """
        reader = cls(streams, reader, *args, **kwargs)
        yield reader
        for stream in reader._streams:
            # Close each remaining stream in the sequence.
            try:
                stream.close()
            except AttributeError:  # no close()
                pass
        return

    def __init__(self, streams, reader, *args, **kwargs):
        """ Initialize this object.
        
        The reader argument is any callable object that takes a stream as its
        only argument and returns a reader to use on that stream, e.g. a reader
        class constructor. The args and kwargs values are passed to the reader 
        function.
    
        Filtering is applied at the ChainReader level, but for filters that
        raise StopIteration this might not be the desired behavior. Raising
        StopIteration from a ReaderSequence filter will halt input from all 
        remaining streams in the sequence. If the intent is to stop input on
        an individual stream, define the callback function to return a Reader 
        that already has the desired filter(s) applied.
    
        """
        def readers():
            """ Yield a reader for each stream. """
            while self._streams:
                stream = self._stream(self._streams[0])
                if stream:
                    # Beware of late binding if the values of args or kwargs
                    # change during iteration.
                    yield reader(stream, *args, **kwargs)
                    stream.close()
                self._streams.popleft()
            return
                   
        super(ChainReader, self).__init__()
        self._streams = deque(streams)
        self._records = chain.from_iterable(readers())
        return
        
    def _get(self):
        """ Return the next parsed record from the sequence.
        
        """
        return self._records.next()
    
    def _stream(self, stream):
        """ Return an open stream based on the given argument.
        
        The argument is either an open stream or a path to open as a text file. 
        Derived classes can override this to support other types of streams, 
        e.g. network streams. Return None to a skip a given item in the 
        sequence.
        
        """
        if isinstance(stream, basestring):
            # Treat this as a file path.
            stream = open(stream, "r")
        return stream


# class ContextualReader(_Reader):
#     """ A reader for contextual lines.
#
#     Fields are determined by context rather than position, and all lines do not
#     necessarily have the same fields, e.g. SHEF data.
#
#     """
#     def _scan(line):
#         """ Scan a line of input.
#
#         """
#         # Return a dict of tokens keyed by the field name.
#         pass
