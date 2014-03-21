# Overview #

The **serial-core** library can be used to read and write serial data
consisting of sequential records of typed fields. Data is read into or written
from dicts that are keyed by field name. The public user interface is defined
in the `serial.core` package.


# Reading Data #

This is fixed-width data consisting of a station identifier, a date string, a
time string, and observations from a sensor array. Each observation has a
floating point value and an optional flag string.

    340010 2012-02-01 00:00 UTC -999.00M -999.00S
    340010 2012-03-01 00:00 UTC   72.00     1.23A
    340010 2012-04-01 00:10 UTC   63.80Q    0.00

This data stream can be read using a `FixedWidthReader`. The reader must be
initialized with a set of field definitions. Each field is associated with a
type and defined by its name and position. For a fixed-width field the position
is a slice specifier, i.e. [begin, end), inclusive of spaces between fields.

    from serial.core import FixedWidthReader
    from serial.core import StringField
    from serial.core import FloatField

    fields = (
        # Ignoring time zone field.
        StringField("stid", (0, 6)),
        StringField("date", (6, 17)),
        StringField("time", (17, 23)),
        FloatField("data1", (27, 35)),
        StringField("flag1", (35, 36)),
        FloatField("data2", (36, 44)),
        StringField("flag2", (44, 45)))

    with FixedWidthReader.open("data.txt", fields) as reader:
        for record in reader:
            print(record)

##  Array Fields ##

If there are a large number of sensor data fields, defining and working with
these fields individually can be tedious. For the sample data the format of 
each sensor field is the same, so they can all be treated as a single array. 
Each array element will have a value and a flag.

An `ArrayField` must be initialized with the field definitions to use for an
array element. The position of the array itself is relative to the entire input
line, but the positions of the element fields are relative to each other.

    from serial.core import ArrayField

    array_fields = (
        # Define each data array element.
        FloatField("value", (0, 8)),  # leading space
        StringField("flag", (8, 9)))

    sample_fields = (
        # Ignoring time zone field.
        StringField("stid", (0, 6)),
        StringField("date", (6, 16)),
        StringField("time", (16, 23)),
        ArrayField("data", (27, 45), array_fields))

    ...

    for record in reader:
        for sensor in record["data"]:
            print(record["date"], sensor["value"], sensor["flag"])


By using a variable-length array, the same format definition can be used if the
the number of sensors varies from file to file or even record to record. A
variable-length array is created by setting its end position to None.
*Variable-length arrays must be at the end of the record*.

    sample_fields = (
        StringField("stid", (0, 7)),
        StringField("date", (7, 17)),
        StringField("time", (17, 23)),
        ArrayField("data", (27, None), array_fields))  # variable length

## Datetime Fields ##

A `DatetimeField` can be used for converting data to a `datetime.datetime`
object. For the sample data, the date and time fields can be treated as a
single `datetime` field. A `DatetimeField` must be initialized with a 
[`datetime` format string][1].

    from serial.core import DatetimeField

    ...

    sample_fields = (
        # Ignoring time zone field.
        StringField("stid", (0, 6)),
        DatetimeField("timestamp", (6, 23), "%Y-%m-%d %H:%M"),
        ArrayField("data", (27, None), array_fields))  # variable length

## Default Values ##

For every input record a Reader will assign a value to each defined field. If 
a field value is blank it is assigned the default value for that field (`None` 
by default). 

    array_fields = (
        FloatField("value", (0, 8)),
        StringField("flag", (8, 9), default="M"))  # replace blanks with M


# Writing Data #

Data is written to a stream using a Writer. Writers implement a `write()` 
method for writing individual records and a `dump()` method for writing a 
sequence of records. Writers use the same field definitions as Readers with 
some additional requirements. 

With some minor modifications the field definitions for reading the sample
data can be used for writing it. In fact, the modified fields can still be used
for reading the data, so a Reader and a Writer can be defined for a given data
format using one set of field definitions. 

    from serial.core import FixedWidthWriter 

    array_fields = (
        FloatField("value", (0, 8), "8.2f"),  # don't forget leading space
        StringField("flag", (8, 9), "1s"))

    sample_fields = (
        # Output fields must be listed in sequential order. 
        StringField("stid", (0, 6), "6s"),
        DatetimeField("timestamp", (6, 23), "%Y-%m-%d %H:%M"),
        StringField("timezone", (23, 27), "3s", default="UTC"),
        ArrayField("data", (27, None), array_fields))

    with open("data.txt", "r") as istream, open("copy.txt", "w") as ostream:
        # Copy "data.txt" to "copy.txt".
        reader = FixedWidthReader(istream, array_fields)
        writer = FixedWidthWriter(ostream, array_fields)
        for record in reader:
            # Write each record to the stream.
            writer.write(record)
        # Or, write all records in a single call: writer.dump(reader) 

## Output Formatting ##

Each field is formatted for output according to its [format string][2]. For
fixed-width output values are fit to the allotted field widths by padding on 
the left or trimming on the right. By using a format width, values can be
positioned within the field. Use a format width smaller than the field width to
specify a left margin and control spacing between field values.

    fields = (
        StringField("stid", (0, 6), "6s"),
        FloatField("value", (6, 14), "7.2f"),  # one character left margin
        ...
    )

## Default Values ##

For every output record a Writer will write a value for each defined field. If 
a field is missing from a record the Writer will use the default value for that 
field (`None` is encoded as a blank field). Default output values must be type-
compatible, e.g. an `IntField` cannot have a default value of "M". 

        
# Delimited Data #

The `DelimitedReader` and `DelimitedWriter` classes can be used for reading and
writing delimited data, e.g. a CSV file.

    340010,2012-02-01 00:00,UTC,-999.00,M,-999.00,S
    340010,2012-03-01 00:00,UTC,72.00,,1.23,A
    340010,2012-04-01 00:10,UTC,63.80,Q,0.00,

Delimited fields are defined in the same way as fixed-width fields except that
scalar field positions are given by field number (starting at 0). Array fields
still use a slice expression. The format string is optional for most field
types because a width is not required.

    from serial.core import DelimitedReader
    from serial.core import DelimitedWriter

    array_fields = (
        FloatField("value", 0, ".2f"),  # don't need width
        StringField("flag", 1))  # default format

    sample_fields = (
        StringField("stid", 0),  # default format
        DatetimeField("timestamp", 1, "%Y-%m-%d %H:%M"),  # format required
        StringField("timezone", 2, default="UTC"),  # default format
        ArrayField("data", (3, None), array_fields))  # variable length

    ...

    delim = ","
    reader = DelimitedReader(istream, sample_fields, delim)
    writer = DelimitedWriter(ostream, sample_fields, delim)


# Initializing Readers and Writers #

For most situations, calling a class's `open()` method is the most convenient 
way to initialize a Reader or Writer. This creates a context manager to be used 
as part of a `with` statement, and upon exit from the context block the stream
associated with the Reader or Writer is closed.

    with DelimitedReader.open("data.csv", fields, ",") as reader:
        # Input file is automatically closed.
        records = list(reader)

If a string is passed to `open()` it is interpreted as a path to be opened as
a plain text file. If another type of stream is needed, open the stream 
explicitly and pass it to `open()`; this stream will be automatically closed.

    stream = GzipFile("data.csv.gz", "r")
    with DelimitedReader.open(stream, fields, ",") as reader:
        # Input stream is automatically closed.
        records = list(reader)

Calling a Reader or Writer constructor directly provides the most control. The
client code is responsible for opening and closing the associated stream. The
constructor takes the same arguments as `open()`, except that the constructor
requires an open stream instead of an optional file path.
        
    stream = GzipFile("data.csv.gz", "r")
    reader = DelimitedReader(stream, fields, ",")
    records = list(reader)
    stream.close()    
        

# Filters #

Filters are used to manipulate data records after they have been parsed by a 
Reader or before they are written by a Writer. A filter is simply a callable 
object that takes a data record as its only argument and returns a record or 
`None`, in which case the record is ignored.

    def month_filter(record):
        """ Filter function to restrict data to records from March. """
        return record if record["timestamp"].month == 3 else None

    ...

    reader.filter(month_filter)  
    records = list(reader)  # read March records only
    
    ...
      
    writer.filter(month_filter)
    writer.dump(records)  # write March records only

## Filter Objects ##

Any callable object can be a filter, including a class that defines a
`__call__()` method. This allows for the creation of more complex filters.

    class MonthFilter(object):
        """ Restrict data to the specified month. """

        def __init__(self, month):
            self._month = month
            return

        def __call__(self, record):
            """ The filter function. """
            return record if record["timestamp"].month == self._month else None

    ...

    reader.filter(MonthFilter(3))  # input is restricted to March

## Altering Records ##

A filter can return a modified version of its input record or a different
record altogether.

    from datetime import timedelta

    class LocalTime(object):
        """ Convert from UTC to local time. """

        def __init__(self, timezone=0):
            self._offset = timedelta(hours=timezone)
            return

        def __call__(self, record):
            """ Filter function. """
            record["timestamp"] += self._offset
            return record  # pass the modified record along

    ...

    reader.filter(LocalTime(-6))  # input is converted from UTC to CST

## Stopping Iteration ##

Returning `None` from a filter will drop individual records, but if the filter 
can determine that there will be no more valid input it can raise a 
`StopIteration` exception to stop input altogether.

    from functools import partial

    def month_filter(month, record):
      """ Restrict input data to a single month. """
      this_month = record["timestamp"].month
      if this_month > month:
          # Data are known to be for one year in chronological order, so there
          # are no more records for the desired month.
          raise StopIteration  # don't do this in an output filter
      return record if this_month == month else None
      
      ...
      
      march_filter = partial(month_filter, 3)  # make this a unary function
      reader.filter(march_filter)
      
## Multiple Filters ##
            
Filters can be chained and are called in order for each record. If a filter
returns `None` the record is immediately dropped. For the best performance 
filters should be ordered from most restrictive (most likely to return `None`) 
to least.

    march_filter = partial(month_filter, 3)
    reader.filter(march_filter)
    reader.filter(LocalTime(-6))
    reader.filter()  # clear existing filters
    reader.filters(march_filter, LocalTime(-6))  # add all filters at once

    reader.filter(march_filter, LocalTime(-6))  # March only, time is CST
    # Or, filters can be added individually. Calling filter() with no
    # arguments clears all filters.

## Predefined Filters

The library defines the `FieldFilter` class for use with Readers and Writers.

        from serial.core import FieldFilter
    
        ...
    
        # Drop all records where the color field is not crimson or cream.
        whitelist = FieldFilter("color", ("crimson", "cream"))
        reader.filter(whitelist)
    
        # Drop all records where the color field is orange.
        blacklist = FieldFilter("color", ("orange",), whitelist=False)
        reader.filter(blacklist)


# Custom Data Formats #

The intent of the `serial.core` library is to provide a framework for dealing
with a wide variety of data formats. The data field definitions are prescribed
by the the format, but filters can be used to build any convenient data model 
on top of that format. Philosophically, reading and writing should be inverse
operations. A Reader and Writer should operate on the same data model such
that the input from a Reader could be passed to a Writer to recreate the input
file.

All the field definitions and filters for a specific format can be encapsulated 
in classes that inherit from the appropriate Reader or Writer, and these
classes can be bundled into a module for that format. There are two categories
of filters, class filters and user filters. Class filters are part of the data 
model, while user filters are optionally applied by client code. Readers apply 
class filters before any user filters, and Writers apply them after any user 
filters. Class filters are not affected by the `filter()` method; instead, 
access them directly using the `_class_filters` attribute.

    """ Module for reading and writing the sample data format. 
        
    """
    from serial.core import DelimitedReader
    from serial.core import DelimitedWriter
    from serial.core import ArrayField
    from serial.core import ConstField
    from serial.core import FloatField  
    from serial.core import StringField

    _SAMPLE_FIELDS = (
        StringField("stid", 0),
        DatetimeField("timestamp", 1, "%Y-%m-%d %H:%M"),
        ConstField("timezone", 2, "UTC"),
        ArrayField("data", (3, None), (
            FloatField("value", 0, ".2f"),
            StringField("flag", 1))))

    _DELIM = ","
    
    class SampleReader(DelimitedReader):
        """ Sample data reader.

        The base class implements the iterator protocol for reading records. All 
        times are converted from UTC to LST during input.

        """
        def __init__(self, stream, timezone=-6):
            
            def lst_filter(record):
                """ Filter function for LST conversion. """
                # Don't need to pass in utc_offset because this is a closure.
                record["timestamp"] += utc_offset  # UTC to LST
                record["timezone"] = "LST"
                return record
            
            super(SampleReader, self).__init__(stream, _SAMPLE_FIELDS, _DELIM)
            utc_offset = timedelta(hours=timezone)  # fractional timezones okay
            self._class_filters.append(lst_filter)  # always applied first 
            return


    class SampleWriter(DelimitedWriter):
        """ Sample data writer.

        The base class defines write() and dump() for writing records. All
        times are converted from LST to UTC during output.

        """
        def __init__(self, stream, timezone=-6):
        
            def utc_filter(record):
                """ Filter function for UTC conversion. """
                # Don't need to pass in utc_offset because this is a closure.
                record["timestamp"] -= utc_offset  # LST to UTC
                record["timezone"] = "UTC"
                return
                
            super(SampleWriter, self).__init__(stream, _SAMPLE_FIELDS, _DELIM)
            utc_offset = timedelta(hours=timezone)  # fractional timezones okay
            self._class_filters(utc_filter)  # always applied last
            return record
            
    # Test the module. 

    with open("data.txt", "r") as istream, open("copy.txt", "w") as ostream:
        # Copy "data.txt" to "copy.txt".
        SampleWriter(ostream).dump(SampleReader(istream))


# Buffers #

Like filters, Buffers allow for postprocessing of input records from a Reader
or preprocessing of output records to a Writer. However, Buffers can operate 
on more than one record at a time. Buffers can be used, for example, to split
or merge records before passing them on. Like Readers and Writers, Buffers
support filtering; records are filtered after they have passed through the 
Buffer.

## Input Buffering ##

An input Buffer is basically a Reader that reads records from another Reader 
(including another input Buffer) instead of lines of text from a stream. An 
input Buffer should derive from the `_ReaderBuffer` base class. It must 
implement a `_queue()` method to process each incoming record, and it may 
override the `_uflow()` method to supply records once the input Reader has been
exhausted.

    from serial.core.buffer import _ReaderBuffer
    
    class MonthlyTotal(_ReaderBuffer):
        """ Combine daily input into monthly records. """
        
        def __init__(self, reader):
            super(MonthlTotal, self).__init__(writer)
            self._buffer = None
            return
        
        def _queue(self, record):
            # Convert incoming daily records to monthly records. The incoming
            # data is assumed to be sorted in chronological order.
            month = record["date"].replace(day=1)
            if self._buffer and self._buffer["date"] == month:
                # Add this record to the current month.
                self._buffer["value"] += record["value"]
            else:
                # Output the previous month and start a new month.
                self._output.append(self._buffer)  # FIFO queue
                self._buffer = record
                self._buffer["date"] = month
            return
                
        def _uflow(self, record):
            # Handle an underflow condition if the output queue is empty and
            # the input reader has been exhausted. No more records are coming,
            # so finish the current month.
            if self._buffer:
                self._output.append(self._buffer)  # FIFO queue
                self._buffer = None  # next call will trigger EOF
            else:
                # This function *must* raise StopIteration on EOF. 
                raise StopIteration 
            return
            
        ...
        
        monthly_records = list(MonthlyTotal(reader))
 
## Output Buffering ##

An output Buffer is basically a Writer that writes records to another Writer
(including another output Buffer) instead of lines of text to a stream. An 
output buffer should derive from the `_WriterBuffer` base class. It must 
implement a `_queue()` method to process records being written to it, and it 
may override the `_flush()` method to finalize processing.
            
    from serial.core.buffer import _WriterBuffer

    class DataExpander(_WriterBuffer):
        """ Output individual elements of an array field. """

        # In addition to the normal Writer interface, the base class defines
        # the close() method to be called by the client code to signal that no 
        # more records will be written. If multiple buffers are chained 
        # together their close() methods must be called in the correct order 
        # (outermost buffer first).

        def __init__(self, writer):
            super(DataExpander, self).__init__(writer)
            return

        def _queue(self, record):
            # Process each outging record.
            for item in record["data"]:
                # Create an output record for each item in the array field.
                item = item.copy()  # output should be free of side effects
                item["stid"] = record["stid"]
                item["timestamp"] = record["timestamp"]
                self._output.append(item)  # FIFO queue
            return
            
        # _WriterBuffer has a _flush() method that can be overridden to 
        # finalize output; is is called when close() is called on the buffer. 
        # For this example, _flush() does not need to do anything.

    ...
    
    DataExpander(writer).dump(reader)  # dump() calls close()

  
# Stream Adaptors #

A Reader's input stream is any object that implements a `next()` method that 
returns a line of text from the stream. A Writer's output stream is any object 
that implements a `write()` method to write a line of text. A Python `file`
object, for example, satisfies the requirements for both types of streams,
depending on what mode it was opened with. The `_IStreamAdaptor` and 
`_OStreamAdaptor` abstract classes in the `stream` module declare the required 
interfaces and can be used to create adaptors for other types of streams. The 
library defines several adaptors as part of the `core` package, such as 
`GzippedIStream`.

    from serial.core import GzippedIStream

    ...
    
    # Read gzipped data; unlike GzipFile this works with streaming data.
    stream = GzippedIStream(urlopen("http://www.data.org/data.csv.gz"))
    with DelimitedReader.open(stream, fields, ",") as reader:
        # The HTTP connection is automatically closed on exit from the with
        # block. 
        data = list(DelimitedReader(stream, fields, ","))

Filters can be applied to streams to manipulate text before it is parsed by
a Reader or after it is written by a Writer. A text filter works just like a
a record filter except that it operates on a line of text instead of a data
record. The library includes the `SliceFilter` and `RegexFilter` text filters.

    from serial.core import FilteredIStream
    from serial.core import SliceFilter  # like FieldFilter for text
    
    ...
    
    # Ignore comments and restrict data to PRCP records. It can be faster to
    # filter at the text level because the amount of data that has to be parsed
    # by the Reader is reduced.
    stream = FilteredIStream(open("data.txt", "r")) 
    stream.filter(lambda line: None if line.startswith("#") else line)
    stream.filter(SliceFilter((21, 25), ("PRCP",)))
    with DelimitedReader.open(stream, fields, ",") as reader:
        records = list(reader)

  
# Tips and Tricks #

## Quoted Strings ##

The `StringField` data type can read and write quoted strings by initializing it
with the quote character to use.

    StringField(quote='"')  # double-quoted string

Quoting for a `DatetimeField` is controlled by its format string:

    DatetimeField("'%Y-%m-%d'")  # single-quoted date string

## Escaped Delimiters ##

Nonsignificant delimiter values need to be escaped when reading data with a
`DelimitedReader`. If the `esc` argument is defined when initializing the 
reader, a delimiter value immediately following the escape value is ignored
when splitting the line into fields. If output written with a `DelimitedWriter` 
needs to be compatible with a `DelimiteReader`, use the appropriate `esc` 
argument when initializing the writer.

    # Write/read escaped delimiters, e.g. "Dallas\, TX"
    writer = DelimitedWriter(stream, fields, delim=",", esc="\\")
    reader = DelimitedReader(stream, fields, delim=",", esc="\\")

## Nonstandard Line Endings ##

By default, lines of text are assumed to end with the platform-specific line
ending, i.e. "\n". Readers expect that ending on each line of text from their
input stream, and Writers append it to each line written to their output
stream. If a Reader's input stream uses a different line ending, or Writer 
output is required to have a different ending, use the `endl` argument with
the appropriate constructor.

    FixedWidthWriter(stream, fields, endl="\r\n")  # force Windows format 

## Header Data ##

Header data is outside the scope of `serial.core`. Client code is responsible
for reading or writing header data from or to the stream before `next()` or
`write()` is called for the first time. For derived classes this is typically
done by the `__init__()` method.

The `BufferedIStream` is useful for parsing streams where the end of the header 
can only be identified by encountering the first data record.

    from serial.core import DelimitedReader
    from serial.core import BufferedIStream

    ...
    
    class DataReader(DelimitedReader):
        """ Read data that has header information. """

        def __init__(self, stream):
            """ Initialize this object. """
            # Header information can be read before or after the base class is
            # initialized, but it must be done before next() is called.
            stream = BufferedIStream(stream)
            for line in stream:
                ...
                if is_data:
                    break
                # Continue reading header information.
                ...
                
            stream.rewind(1)  # reposition at first data record
            super(DataReader, self).__init__(stream, _FIELDS, _DELIM)
            return
 
## Mixed-Type Data ##

Mixed-type data fields must be defined as a `StringField` for stream input and
output, but filters can be used to convert to/from multiple Python types based
on the field value.

    def missing_filter(record):
        """ Input filter for numeric data that's 'M' if missing. """
        try:
            record["mixed"] = float(record["mixed"])
        except ValueError:  # conversion failed, value is 'M'
            record["mixed"] = None  # a more convenient value for missing data
        return record

## Combined Fields ##

Filters can be used to map a single field in the input/output stream to/from
multiple fields in the data record (or vice versa).

    def timestamp_filter(record):
        """ Output filter to split timestamp into separate fields. """
        # The data format defines separate "date" and "time" fields instead of
        # the combined "timestamp". The superfluous timestamp field will be
        # ignored by the Writer, so deleting it is not necessary.
        record = record.copy()  # write() shouldn't have any side effects
        record["date"] = record["timestamp"].date()
        record["time"] = record["timestamp"].time()
        return record

 
<!-- REFERENCES -->
[1]: http://docs.python.org/2/library/datetime.html#strftime-strptime-behavior "datetime class"
[2]: http://docs.python.org/2/library/string.html#formatspec "format strings"
