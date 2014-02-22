""" Reader types.

Readers convert lines of text to data records.

"""
from __future__ import absolute_import

from contextlib import contextmanager
from functools import partial
from itertools import chain
from re import compile

from ._util import Field

__all__ = ("DelimitedReader", "FixedWidthReader", "ReaderSequence")


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
        # This does not effect class filters.
        if not callbacks:
            self._user_filters = []
        else:
            self._user_filters.extend(callbacks)
        return

    def next(self):
        """ Return the next filtered record.

        This implements the Python iterator protocol.

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
        """ Iterate over all filtered input records.

        """
        return self

    def _get(self):
        """ Get the next parsed record from the input source.

        This is the last step before any filters get applied to the record and
        it's returned to the client. The implementation must raise a
        StopIteration exception to signal that input has been exhausted.

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
        self._fields = [Field(*args) for args in fields]
        self._endl = endl
        return

    def _get(self):
        """ Return the next parsed record from the stream.

        This function implements the Pyhthon iterator idiom and raises a
        StopIterator exception when the input stream is exhausted.

        """
        tokens = self._split(self._stream.next().rstrip(self._endl))
        return dict((field.name, field.dtype.decode(token)) for (field, token)
                     in zip(self._fields, tokens))

    def _split(self, line):
        """ Split a line of text into a sequence of tokens.

        """
        raise NotImplementedError


class DelimitedReader(_TabularReader):
    """ A reader for delimited lines of text.

    The position of each scalar field is be given as an integer index, and the
    position of an array field is the pair [beg, end).

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
            patt = "(?<!{0:s}){1:s}".format(esc, delim).encode("string-escape")
            self._tokenize = compile(patt).split    
            patt = "{0:s}{1:s}".format(esc, delim).encode("string-escape")
            self._unescape = partial(compile(patt).sub, delim)
        else:
            self._tokenize = lambda line: line.split(delim)
            self._unescape = None
        return

    def _split(self, line):
        """ Split a line of text into a sequence of tokens.

        Lines are split at each occurrence of the delimiter; the delimiter is
        discarded.

        """
        tokens = map(self._unescape, self._tokenize(line))
        return tuple(tokens[field.pos] for field in self._fields)


class FixedWidthReader(_TabularReader):
    """ A reader for lines of text delineated by character position.

    The character position of each field is given as the pair [beg, end).

    """
    def _split(self, line):
        """ Split a line of text into a sequence of tokens.

        Lines are split based on the specified position of each field.

        """
        return tuple(line[field.pos] for field in self._fields)


class ReaderSequence(_Reader):
    """ Iterate over a sequence of files/streams as a single sequence.
    
    """
    def __init__(self, callback, *input):
        """ Initialize this object.
        
        The callback argument is any callable object that takes a stream as its
        only argument and returns a Reader to use on that stream, e.g. a 
        Reader constructor. The remaining arguments are either open streams or
        paths to open as plain text files. Each input stream is closed once it
        has been exhausted.
        
        Filtering is applied at the ReaderSequence level, but for filters that
        raise StopIteration this might not be the desired behavior. Halting
        iteration at this level effects all subsequent streams. If the intent
        is to stop iteration for each individual stream, define the callback 
        function to return a Reader that already has the appropriate filter(s)
        applied.
        
        """
        super(ReaderSequence, self).__init__()
        self._input = list(input)
        self._callback = callback 
        self._reader = None
        return
        
    def _get(self):
        """ Return the next parsed record from the sequence.
        
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
        return
        
    def _open(self):
        """ Open the next stream in the sequence.
        
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
