""" Writer types.

Writers convert data records to lines of text.

"""
from ._util import make_fields

__all__ = ("DelimitedWriter", "FixedWidthWriter")


class SerialWriter(object):
    """ Abstract base class for all serial data writers.
    
    Serial data consists of individual records stored as lines of text.
            
    """    
    def __init__(self, stream, endl):
        """ Initialize this object.
        
        The stream can be any object that has a write() method.
        
        """
        self._stream = stream
        self._endl = endl
        return
    
    def _putline(self, line):
        """ Write a line to the stream.
        
        """
        self._stream.write(line + self._endl)
        return
        
        
class TabularWriter(SerialWriter):
    """ Abstract base class for tabular data writers.
    
    Tabular data is organized fields such that each field occupies the same
    position in each record. One line of text corresponds to a one complete
    record.
    
    """   
    def __init__(self, stream, fields, endl="\n"):
        """ Initialize this object.
        
        """
        super(TabularWriter, self).__init__(stream, endl)
        self._fields = make_fields(fields)
        self._filters = []
        return
    
    def write(self, record):
        """ Write a record to the output stream.
        
        """
        for func in self._filters:
            if not func(record):
                return
        tokens = [field.dtype.encode(record.get(field.name)) for field in 
                  self._fields]
        return self._putline(self._merge(tokens))
        
    def filter(self, func=None):
        """ Add a filter to this object or clear all filters.
        
        A filter is a function that accecpts a data record as its argument.
        The function returns to True to accept the argument or False to reject
        it (it will be not passed to the user). Because the record is a dict,
        the function can also modify it in place. Records are passed through
        all filters in the order they were added.
        
        Calling the function with no arguments will clear all filters.
        
        """
        if func is None:
            self._filters = []
        else:
            self._filters.append(func)
        return

    def _merge(self, tokens): 
        """ Create a line of text from a sequence of tokens.
        
        """
        raise NotImplementedError
        

class DelimitedWriter(TabularWriter):
    """ A writer for fields delineated by a delimiter.
    
    The position of each scalar field is be given as an integer index, and the
    position of an array field is the pair [beg, end).
    
    """   
    def __init__(self, stream, fields, delim=" ", endl="\n"):
        """ Initialize this object.
        
        At this time there is no escaping of characters in the input records 
        that match the delimiter; this may cause issues when trying to parse
        the resulting output.
        
        """
        super(DelimitedWriter, self).__init__(stream, fields, endl)
        self._delim = delim
        return
        
    def _merge(self, tokens):
        """ Create a line of text from a sequence of tokens.
        
        """
        return self._delim.join(tokens)


class FixedWidthWriter(TabularWriter):
    """ A writer for fields delineated by character position.
    
    The character position of each field is given as the pair [beg, end).
    
    """
    def _merge(self, tokens):
        """ Create a line of text from a sequence of tokens.
        
        """
        # The character positions in self.fields don't matter; tokens must be
        # in the correct order, and each token must be the correct width for
        # that field. The DataType format for a fixed-width field *MUST* have
        # a field width, e.g. '8s'.
        return "".join(tokens)
        
        