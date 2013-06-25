# serial.core Tutorial #

## Reading Data ##

Consider the following snippet of data:

    340010 2012-02-01 00:00 UTC -999.00M -999.00S
    340010 2012-03-01 00:00 UTC   72.00     1.23A
    340010 2012-04-01 00:10 UTC   63.80Q    0.00


This is fixed-width data consisting of a station identifier, a date string, a
time string, and observations from a sensor array. Each observation has a
floating point value and an optional flag string.

This data stream can be read using a `FixedWidthReader`. The reader must be
initialized with a set of field definitions. Each field is defined by its name,
position, and data type. For a fixed-width field the position is given by its
character positions, i.e. a [begin, end) pair:

    from serial.core import FixedWidthReader
    from serial.core import StringType
    from serial.core import FloatType

    fields = (
        # Ignoring time zone field.
        ("stid", (0, 7), StringType()),
        ("date", (7, 17), StringType()),
        ("time", (17, 23), StringType()),
        ("data1", (27, 35), FloatType()),
        ("flag1", (35, 36), StringType()),
        ("data2", (36, 44), FloatType()),
        ("flag2", (44, 45), StringType()))

    with open("data.txt", "r") as istream:
        for record in FixedWidthReader(istream, fields):
            print(record)


###  Array Fields ###

If there are a large number of sensor data fields, defining and working with
these fields individually can be tedious. For the sample data the format of 
each sensor field is the same, so they can all be treated as a single array. 
Each array element will have a value and a flag.

An `ArrayType` field must be initalized with the field definitions to use for
an array element. The position of the array itself is relative to the entire
input line, but the positions of the element fields are relative to each other.

    from serial.core import ArrayType

    array_fields = (
        ("value", (0, 8), FloatType()),  # don't forget leading space
        ("flag", (8, 9), StringType()))

    sample_fields = (
        # Ignoring time zone field.
        ("stid", (0, 7), StringType()),
        ("date", (7, 17), StringType()),
        ("time", (17, 23), StringType()),
        ("data", (27, 45), ArrayType(array_fields)))

    ...

    for record in reader:
        for sensor in record["data"]:
            print(record["date"], sensor["value"], sensor["flag"])


By using a variable-length array, the same format definition can be used if the
the number of sensors varies from file to file or even record to record. A
variable-length array is created by setting its end position to None.
*Variable-length arrays must be at the end of the record*.

    sample_fields = (
        ("stid", (0, 7), StringType()),
        ("date", (7, 17), StringType()),
        ("time", (17, 23), StringType()),
        ("data", (27, None), ArrayType(array_fields)))  # variable length


### Datetime Fields ###

The `DatetimeType` can be used for converting data to a `datetime.datetime`
object. For the sample data, the date and time fields can be treated as a
single `datetime` field. A `DatetimeType` must be initialized with a 
[`datetime` format string][1].

    from serial.core import DatetimeType

    ...

    sample_fields = (
        # Ignoring time zone field.
        ("stid", (0, 6), StringType()),
        ("timestamp", (6, 23), DatetimeType("%Y-%m-%d %H:%M")),
        ("data", (27, None), ArrayType(array_fields)))  # variable length


### Default Values ###

During input all fields in a record are assigned a value. If a field is blank
it is given the default value assigned to that field (`None` by default). 

    array_fields = (
        ("value", (0, 8), FloatType()),
        ("flag", (8, 9), StringType(default="M")))  # replace blanks with M


## Writing Data ##

Data is written to a stream using a Writer. Writers implement a `write()` 
method for writing individual records and a `dump()` method for writing a 
sequence of records. 

Writers use the same field definitions as Readers with some additional 
requirements. A data type can be initialized with a [format string][2]; this is 
ignored by Readers, but it is used by Writers to convert a Python value to 
text. Each data type has a default format, but for `FixedWidthWriter` fields a 
format string with the appropriate field width (inclusive of spaces between
fields) **must** be specified.

For the `FixedWidthReader` example the time zone field was ignored. However,
when defining fields for a `FixedWidthWriter`, every field must be defined,
even if it's blank. Also, fields must be listed in their correct order.

A Writer will output a value for each of its fields with every data record. If
a field is missing from a data record the Writer will use the default value for 
that field (`None` is encoded as a blank field). For input a default field 
value can be anything, but for output it must be type-compatible, e.g. 
`IntType(default="M")` is an error. Fields in the record that do not correspond 
to an output field are ignored.

With some minor modifications the field definitions for reading the sample
data can be used for writing it. In fact, the modified fields can still be used
for reading the data, so a Reader and a Writer can be defined for a given data
format using one set of field definitions:

    from serial.core import FixedWidthWriter 

    array_fields = (
        ("value", (0, 8), FloatType("8.2f")),  # don't forget leading space
        ("flag", (8, 9), StringType("1s")))

    sample_fields = (
        ("stid", (0, 7), StringType("7s")),  # trailing space
        ("timestamp", (7, 23), DatetimeType("%Y-%m-%d %H:%M")),
        ("timezone", (23, 27), StringType(">4s", default="UTC")),
        ("data", (27, None), ArrayType(array_fields)))  # no format string

    with open("data.txt", "r") as istream, open("copy.txt", "w") as ostream:
        # Copy "data.txt" to "copy.txt".
        reader = FixedWidthReader(istream, sample_fields)
        writer = FixedWidthWriter(ostream, sample_fields)
        for record in reader:
            # Write all records in one call: writer.dump(reader)
            del record["timezone"]  # rely on default value
            writer.write(record)
        
## Delimited Data ##

The `DelimitedReader` and `DelimitedWriter` classes can be used for reading and
writing delimited data, e.g. a CSV file:

    340010,2012-02-01 00:00,UTC,-999.00,M,-999.00,S
    340010,2012-03-01 00:00,UTC,72.00,,1.23,A
    340010,2012-04-01 00:10,UTC,63.80,Q,0.00,


Delimited fields are defined in the same way as fixed-width fields except that
the field positions are given by index number instead of character positions.
Scalar field positions are a single number while array field positions are a
[begin, end) pair. The format string is optional for most field types because a
width is not required:

    from serial.core import DelimitedReader
    from serial.core import DelimitedWriter

    array_fields = (
        ("value", 0, FloatType(".2f")),  # don't need width
        ("flag", 1, StringType()))  # default format

    sample_fields = (
        ("stid", 0, StringType()),  # default format
        ("timestamp", 1, DatetimeType("%Y-%m-%d %H:%M")),  # format required
        ("timezone", 2, StringType(default="UTC")),  # default format
        ("data", (3, None), ArrayType(array_fields)))  # variable length

    ...

    delim = ","
    reader = DelimitedReader(istream, sample_fields, delim)
    writer = DelimitedWriter(ostream, sample_fields, delim)

        
## Filters ##

Filters are used to manipulate data records after they have been parsed by a 
Reader or before they are written by a Writer. A filter is simply a callable 
object that takes a data record as its only argument and returns a record or 
`None`, in which case the record is ignored: 

    def month_filter(record):
        """ Filter function to restrict data to records from March. """
        return record if record["timestamp"].month == 3 else None

    ...

    reader.filter(month_filter)  
    records = list(reader)  # read March records only
    
    ...
      
    writer.filter(month_filter)
    writer.dump(records)  # write March records only


### Filter Objects ###

Any callable object can be a filter, including a class that defines a
`__call__()` method. This allows for the creation of more complex filters:

    class MonthFilter(object):
        """ Restrict input to the specified month. """

        def __init__(self, month):
            self._month = month
            return

        def __call__(self, record):
            """ The filter function. """
            return record if record["timestamp"].month == self._month else None

    ...

    reader.filter(MonthFilter(3))  # input is restricted to March


### Altering Records ###

A filter can return a modified version of its input record or a different
record altogether.

    from datetime import timedelta

    class LocalTime(object):
        """ Convert from UTC to local time. """

        def __init__(self, offset):
            self._offset = timedelta(hours=offset)
            return

        def __call__(self, record):
            """ Filter function. """
            record["timestamp"] += self._offset
            return record  # pass the modified record

    ...

    reader.filter(LocalTime(-6))  # input is converted from UTC to CST

    
### Stopping Iteration ###

Returning `None` from a filter will drop individual records, but input can be
stopped altogether by raising a `StopIteration` exception. When filtering data 
by time, if the data are in chronological order it doesn't make sense to
continue reading from the stream once the desired time period has been passed:

    class MonthFilter(object):
        """ Restrict input data to a single month. """

        def __init__(self, month):
            """ Initialize this object. """
            self._month = month
            return

        def __call__(self, record):
            """ Filter function. """
            month = record["timestamp"].month
            if month > self._month:
                # Data are for one year in chronological order so there are no 
                # more records for the desired month.
                raise StopIteration  # don't do this in an output filter
            return record if month == self._month else None

            
### Multiple Filters ###
            
Filters can be chained and are called in order for each record. If a filter
returns `None` the record is immediately dropped. For
the best performance filters should be ordered from most restrictive (most
likely to return `None`) to least.

    reader.filter(MonthFilter(3), LocalTime(-6))  # March only, time is CST


Two filters are defined by the library:

    from serial.core import BlacklistFilter
    from serial.core import WhitelistFilter
    
    ...
    
    # Reject all records where the color field is orange or black.
    reader.filter(BlacklistFilter("color", ("orange", "black")))
    
    # Reject all records where the color field is not crimson or cream.
    reader.filter(WhitelistFilter("color", ("crimson", "cream")))


## Extending Core Classes ##

All the field definitions and filters for a specific format can be encapsulated
in a class that inherits from the appropriate Reader or Writer, and these
classes can be bundled into a module for that format.

    """ Module for reading and writing the sample data format. """

    from serial.core import DelimitedReader
    from serial.core import DelimitedWriter
    from serial.core import ArrayType
    from serial.core import ConstType
    from serial.core import FloatType  
    from serial.core import StringType

    _ARRAY_FIELDS = (
      ("value", 0, FloatType(".2f")),
      ("flag", 1, StringType()))

    _SAMPLE_FIELDS = (
      ("stid", 0, StringType()),
      ("timestamp", 1, DatetimeType("%Y-%m-%d %H:%M")),
      ("timezone", 2, ConstType("UTC")),
      ("data", (3, None), ArrayType(_ARRAY_FIELDS)))

    _DELIM = ","
    
    class SampleReader(DelimitedReader):
        """ Sample data reader.

        Base class implements iterator protocol for reading records.

        """
        def __init__(self, stream, offset=-6):
            super(SampleReader, self).__init__(stream, _SAMPLE_FIELDS, _DELIM)
            self._offset = timedelta(hours=offset)  # offset from UTC
            self.filter(self._lst_filter)
            return

        def _lst_filter(self, record):
            """ Filter function for LST conversion. """
            record["timestamp"] += self._offset  # UTC to LST
            record["timezone"] = "LST"
            return record

    class SampleWriter(DelimitedWriter):
        """ Sample data writer.

        Base class defines write() and dump() for writing records.

        """
        def __init__(self, stream, offset=-6):
            super(SampleWriter, self).__init__(stream, _SAMPLE_FIELDS, _DELIM)
            self._offset = timedelta(hours=offset)  # offset from UTC
            self.filter(self._utc_filter)
            return record

        def _utc_filter(self, record):
            """ Filter function for UTC conversion. """
            record["timestamp"] -= self._offset  # LST to UTC
            record["timezone"] = "UTC"
            return
    
    
    # Test the module. 

    with open("data.txt", "r") as istream, open("copy.txt", "w") as ostream:
        # Copy "data.txt" to "copy.txt".
        SampleWriter(ostream).dump(SampleReader(istream))


## Buffers ##

Like filters, Buffers allow for postprocssing of input records or preprocessing
of output records. However, Buffers are designed to work on groups of records,
and they are implemented as a wrapper around a Reader or Writer (or another 
Buffer). A Buffer implementation should be derived from `_ReaderBuffer` or
`_WriterBuffer`. A common use case for a Buffer is to map a single incoming 
record to multiple outgoing records. Buffers can also be used for sorting or
aggregation (but Python's built-in [`sorted()`][3] or [`map()`][4] and 
[`itertools.groupby()`][5] functions are preferred for those applications). 

    from serial.core.buffer import _ReaderBuffer
    
    class Expander(_ReaderBuffer):
        """ Expand an incoming record into multiple outgoing records.
        
        The base class implements the iterator protocol for accessing the new
        records.
        
        """
        def __init__(self, reader):
            """ Initialize this object.
            
            The reader can be a Reader object or another _ReaderBuffer.
            
            """
            super(Expander, self).__init__(reader)
            ...
            return
        
        def _read(self, record)
            """ _ReaderBuffer: Process each incoming record.
            
            This must be defined by all derived classes.
            
            """
            # Generate a sequence of multiple records from each incoming record
            # and queue them for output.
            ...
            self._output.extend(record_list)  # FIFO
            return

        def _flush(self):
            """ Finalize the buffer.
        
            This is called when the input reader is exhausted. The default 
            version does nothing, and derived classes should override it as
            necessary.
        
            """
            # This will often be used by an aggregator to flush any remaining
            # records in its buffer to the output queue, but in this case 
            # it doesn't need to do anything.
            return            


## Stream Adaptors ##

Readers and Writers are both initialized with stream arguments. A Reader's
input stream is any object that implements a `next()` method that returns a
line of text from the stream. A Writer's output stream is any object that 
implements a `write()` method to write a line of text. A Python `file` object 
satisfies the requirements for both types of streams. The `_IStreamAdaptor` and 
`_OStreamAdaptor` abstract classes declare the required interfaces and can be 
used to create adaptors for other types of streams, *e.g.* binary data: 

    from serial.core.stream import _IStreamAdaptor
    from serial.core.stream import _OStreamAdaptor

    class BinaryStream(_IStreamAdaptor, _OStreamAdaptor):
        """ Interface for a binary data stream.

        This can be used as the stream for a Reader or Writer.

        """
        ...

        def next(self):
            """ IStreamAdaptor: Return a line of text from the stream. """
            ...
            return line

        def write(self, line):
            """ OStreamAdaptor: Write a line of text to the stream. """
            ...
            return


## Tips and Tricks ##

### Quoted Strings ###

The `StringType` data type can read and write quoted strings by initializing it
with the quote character to use:

    StringType(quote='"')  # double-quoted string

Quoting for a `DatetimeType` is controlled by its format string:

    DatetimeType("'%Y-%m-%d'")  # single-quoted date string


### Nonstandard Line Endings ###

By default, lines of text are assumed to end with the newline character, but 
other line endings can be specified for both Readers and Writers:

    writer = DelimitedWriter(stream, fields, delim, endl="")  # no trailing \n


### Header Data ###

Header data is outside the scope of `serial.core`. Client code is responsible
for reading or writing header data from or to the stream before `next()` or
`write()` is called for the first time. For derived classes this is typically
done by the `__init__()` method.

The `IStreamBuffer` class is a stream adaptor that adds buffering to input
streams. This is useful for parsing streams where the end of the header can
only be identified by encountering the first data record:

    from serial.core import DelimitedReader
    from serial.core import IStreamBuffer

    ...
    
    class DataReader(DelimitedReader):
        """ Read data that has header information. """

        def __init__(self, stream):
            """ Initialize this object. """
            # Header information can be read before or after the base class is
            # initialized, but it must be done before next() is called.
            stream = IStreamBuffer(stream)
            for line in stream:            
                # At the end of this loop the first data record has already
                # been read.
                ...
                if is_data:
                    break
            stream.rewind(1)  # reposition at first data record
            super(DataReader, self).__init__(stream, _FIELDS, _DELIM)
            return

 
### Mixed-Type Data ###

Mixed-type data fields must be defined as a `StringType` for stream input and
output, but filters can be used to convert to/from multiple Python types based
on the field value.

    def missing_filter(record):
        """ Input filter for numeric data that's 'M' if missing. """
        try:
            record["mixed"] = float(record["mixed"])
        except ValueError:  # conversion failed, value is 'M'
            record["mixed"] = None  # a more convient value for missing data
        return record


### Combined Fields ###

Filters can be used to map a single field in the input/output stream to/from
multiple fields in the data record, or vice versa:

    def timestamp_filter(record):
        """ Output filter to split timestamp into separate fields. """
        # The data format defines separate "date" and "time" fields instaad of
        # the combined "timestamp". The superfluous timestamp field will be
        # ignored by the Writer so deleting it is redundant.
        record = record.copy()  # write() shouldn't have any side effects
        record["date"] = record["timestamp"].date()
        record["time"] = record["timestamp"].time()
        return record


### Compressed Data ###

The `IStreamZlib` stream adapter can be used to read any zlib-compressed data
including gzip files. Unlike the built-in Python `gzip.GzipFile`, an 
`IStreamZlib` can handle streaming data such as network files:

    from conxtextlib import closing
    from serial.core import IStreamZlib

    ...

    with closing(urllib2.urlopen("http://data.org/path/data.gz")) as istream:
        reader = DelimitedReader(IStreamZlib(istream), fields)
    

### Low Level Text Manipulation ###

Stream adaptors can be used to manipulate text before it is parsed by a Reader
or after it has been processed by a Writer:

    class TextPreprocessor(_IStreamAdaptor):
        """ Remove comments and blanks lines from an input stream. """
        def __init__(self, stream):
            """ Initialize this object. """
            self._stream = stream
            return
    
        def next(self):
            """ Return the next line of data from the stream. """
            while True:  # repeat until a data line is encountered or EOF
                line = self._stream.next()
                if line.strip() and not line.startswith("#"):
                    return line
 
<!-- REFERENCES -->
[1]: http://docs.python.org/2/library/datetime.html#strftime-strptime-behavior "datetime class"
[2]: http://docs.python.org/2/library/string.html#formatspec "format strings"
[3]: http://docs.python.org/2/library/functions.html#sorted "sorted() function"
[4]: http://docs.python.org/2/library/functions.html#map "map() function"
[5]: http://docs.python.org/2/library/itertools.html?#itertools.groupby "groupby() function"