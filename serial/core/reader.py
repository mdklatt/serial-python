""" Reader types.

Readers convert lines of text to data records.

"""
from __future__ import absolute_import

from contextlib import contextmanager
from functools import partial
from itertools import chain
from re import compile

__all__ = ("DelimitedReader", "FixedWidthReader", "SequenceReader",
           "ReaderSequence")


class _Reader(object):
    """ Abstract base class for all serial data readers.

    Serial data consists of sequential records. A _Reader provides an iterator
    interface for reading serial data and allows for precprocessing of the data
    using filters.

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

        A filter is a callable object that accepts a data record as its only
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
        """ Read the next record while applying filtering o.

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
    def open(cls, expr, *args, **kwargs):
        """ Create a runtime context for a _TabularReader and its stream.
        
        The arguments are passed to the reader's constructor, except that the
        first argument is either an open stream or a file path that is used to 
        open a text file for reading. In both cases the stream will be closed
        upon exit from the context block.
        
        """
        # This assumes that first argument for all derived class constructors
        # is the stream; if not, this will need to be overridden.
        try:
            stream = open(expr, "r")
        except TypeError:  # not a string
            stream = expr
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


class SequenceReader(_Reader):
    """ Read a sequence of streams as a single series of records.
    
    The SequenceReader opens streams as necessary and closes them once they
    have been reader.
    
    """
    @classmethod
    @contextmanager
    def open(cls, streams, callback, *args, **kwargs):
        """ Create a runtime context for a SequenceReader and its streams.
        
        The arguments are passed to the class constructor. Each stream is
        closed once it has been exhausted, and any open streams remaining in
        the sequence will be closed upon exit from the context block.
        
        """
        reader = cls(streams, callback, *args, **kwargs)
        yield reader
        reader.close()
        return

    def __init__(self, streams, callback):
        """ Initialize this object.
        
        The callback argument is any callable object that takes a stream as its
        only argument and returns a reader to use on that stream, e.g. a reader
        class constructor.
    
        Filtering is applied at the SequenceReader level, but for filters that
        raise StopIteration this might not be the desired behavior. Raising
        StopIteration from a ReaderSequence filter will halt input from all 
        remaining streams in the sequence. If the intent is to stop input on
        an individual stream, define the callback function to return a Reader 
        that already has the desired filter(s) applied.
    
        """
        def readers():
            """ Yield a reader for each stream. """
            for expr in self._streams:
                stream = self._stream(expr)
                if not stream:
                    continue
                yield callback(stream)
                stream.close()
            return
                   
        super(SequenceReader, self).__init__()
        self._streams = iter(streams) 
        self._records = chain.from_iterable(readers())
        return
        
    def close(self):
        """ Close any remaning streams in the sequence.
        
        """
        for stream in self._streams:
            try:
                stream.close()
            except AttributeError:  # no close()
                pass
        self._streams = None
        return
        
    def _get(self):
        """ Return he next parsed record from the sequence.
        
        """
        return self._records.next()
    
    def _stream(self, expr):
        """ Return an open stream using the given expression.
        
        The expression is either a path to open as a text file or an already 
        open stream. Derived classes can override this to support other types
        of streams, e.g. network streams.
        
        """
        try:
            # Try to open a path as a text file.
            stream = open(expr, "r")
        except TypeError:
            # Not a string, assume it's an open stream.
            stream = expr
        return stream


class ReaderSequence(_Reader):
    """ Iterate over multiple input sources as a single sequence of records.
    
    """
    def __init__(self, callback, *input):
        """ Initialize this object.
        
        The callback argument is any callable object that takes a stream or
        as its only argument and returns a Reader to use on that stream, e.g. a 
        Reader constructor. The remaining arguments are either open streams or
        paths to open as plain text files. Each stream is closed once it has
        been exhausted.
        
        Filtering is applied at the ReaderSequence level, but for filters that
        raise StopIteration this might not be the desired behavior. Raising
        StopIteration from a ReaderSequence filter will halt input from all 
        remaining streams in the sequence. If the intent is to stop input on
        an individual stream, define the callback function to return a Reader 
        that already has the desired filter(s) applied.
        
        """
        from warnings import warn
        message = "ReaderSequence is deprecated; use SequenceReader instead"
        warn(message, DeprecationWarning)
        
        super(ReaderSequence, self).__init__()
        self._input = list(input)
        self._callback = callback 
        self._reader = None
        return
        
    def _get(self):
        """ Get the next parsed record from the sequence.
        
        This is called before any filters have been applied. A StopIteration 
        exception is raised when all streams in the sequence have been 
        exhausted.
        
        """
        while True:
            # Repeat until a record is returned or there are no more streams
            # to open. If the current reader is None or exhuasted try to open
            # a new stream.
            try:
                return self._reader.next()
            except AttributeError:
                if self._reader is not None:
                    # The reader has been initialized but doesn't have a next()
                    # method.
                    raise
            except StopIteration:
                # The reader is exhausted.
                pass
            self._open()
        
    def _open(self):
        """ Create a reader for the next stream in the sequence.
        
        """
        if self._reader:
            # Close the open stream.
            self._input.pop(0).close()
        try:
            # Try to open a path as a text file.
            self._input[0] = open(self._input[0], "r")
        except TypeError:
            # Not a string, assume it's an open stream.
            pass
        except IndexError:
            # No more streams.
            raise StopIteration
        self._reader = self._callback(self._input[0])
        return 
        
    def __enter__(self):
        """ Enter a context block.
        
        """ 
        return self
        
    def __exit__(self, etype=None, value=None, trace=None):
        """ Exit a context block.
        
        """
        # The exception-handling arguments are ignored; if the context exits 
        # due to an exception it will be passed along to the caller.
        for stream in self._input:
            try:
                stream.close()
            except AttributeError:  # no close
                continue
        return


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
