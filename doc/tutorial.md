# Tutorial #


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
character positions as a [begin, end) pair, inclusive of any spaces between
fields.

    from serial.core import FixedWidthReader
    from serial.core import StringType
    from serial.core import FloatType

    fields = (
        ("stid", (0, 6), StringType()),
        ("date", (6, 17), StringType()),
        ("time", (17, 23), StringType()),
        ("data1", (27, 35), FloatType()),
        ("flag1", (35, 36), StringType()),
        ("data2", (36, 44), FloatType()),
        ("flag2", (44, 45), StringType()))

    stream = open("data.txt", "r")
    reader = FixedWidthReader(stream, fields)
    for record in reader:
        print(record)


###  Array Fields ###

If there are a large number of sensor data fields, defining and working with
these fields individually can be error-prone and tedious. For the sample data
the format of each sensor field is the same, so they can all be treated as a
single array. Each array element will have a value and a flag.

An `ArrayType` field must be initalized with the field definitions to use for
each array element. The position of the array itself is relative to the entire
input line, but the positions of the element fields are relative to an
individual element.

    from serial.core import ArrayType

    data_fields = (
        ("value", (0, 8), FloatType()),  # don't forget leading space
        ("flag", (8, 9), StringType()))

    sample_fields = (
        # Ignoring time zone field.
        ("stid", (0, 6), StringType()),
        ("date", (6, 17), StringType()),
        ("time", (17, 23), StringType()),
        ("data", (27, 45), ArrayType(data_fields)))

    stream = open("data.txt", "r")
    reader = FixedWidthReader(stream, fields)
    for record in reader:
        for sensor in record["data"]
            print(sensor["value"], sensor["flag"])

By using a variable-length array, the same format definition can be used if the
the number of sensors varies from file to file or even record to record. A
variable-length array is created by setting its end position to None.
*Variable-length arrays must be at the end of the record*.

    sample_fields = (
        ("stid", (0, 6), StringType()),
        ("date", (6, 17), StringType()),
        ("time", (17, 23), StringType()),
        ("data", (27, None), ArrayType(data_fields)))  # variable length

    ...

    for record in reader:
        print("total sensors: {0:d}".format(len(record["data"])))
        for sensor in record["data"]
            print(sensor["value"], sensor["flag"])


### Datetime Fields ###

The `DatetimeType` can be used for converting data to a `datetime.datetime`
object. For the sample data, the date and time fields can be treated as a
single `datetime` field. A `DatetimeType` must be initialized with a `datetime`
[format string][1].

    from serial.core import DatetimeType

    ...

    sample_fields = (
        # Ignoring time zone field.
        ("stid", (0, 6), StringType()),
        ("timestamp", (6, 23), DatetimeType("%Y-%m-%d %H:%M:%S")),
        ("data", (27, None), ArrayType(data_fields)))  # variable length


### Default Values ###

During input, all fields in a record are assigned a value. If a field is blank
it is given a value of None. A data type can be assigned a default value; this
value will be used instead of None if the field is blank. The default value 
should be appropriate to that type, *e.g.* an `IntType` field should not have a 
default value of "N/A".

    data_fields = (
        ("value", (0, 8), FloatType()),
        ("flag", (8, 9), StringType(default="M")))  # replace blanks with M


### Filters ###

Filters are used to manipulate data records after they have been parsed but
before they are returned by the iterator. A filter is simply a callable object
that takes a data record as its only argument and returns a record or None.

    def month_filter(record):
        """ Filter function to restrict data to records from March. """
        return record if record["timestamp"].month == 3 else None

    ...

    reader.filter(month_filter)  # add this filter to the reader
    for record in reader:
        # Only records from March are shown.
        print(record)


### Advanced Filtering ###

Any callable object can be a filter, including a class that defines a
`__call__()` method. This allows for the creation of more complex filters.

    class MonthFilter(object):
        """ Restrict input to the specified month. """

        def __init__(self, month):
            self._month = month
            return

        def __call__(self, record):
            """ The filter function. """
            return record if record["timestamp"].month == 3 else None

    ...

    reader.filter(MonthFilter(3))  # input is restricted to March

A filter can return a modified version of its input record or a different
record altogether.

    from datetime import timedelta

    class LocalTime(object):
        """ Convert from UTC to local time. """

        def __init__(self, local)
            self._offset = timedelta(hours=local)
            return

        def __call__(self, record):
            """ Filter function. """
            record["timestamp"] += self._offset
            return record  # pass the modified record

    ...

    reader.filter(LocalTime(-6))  # input is converted from UTC to CST

Returning None from a filter will drop individual records, but input can be
stopped altogether by raising a StopIteration exception. When filtering data by
by time, if the data are in chronological order it doesn't make sense to
continue reading from the stream once the desired time period has been passed:

    class MonthFilter(object):
        """ Restrict input data to a single month. """

        def __init__(self, month):
            self._month = month
            return

        def __call__(self, record):
            """ Filter function. """
            month = record["timestamp"].month
            if month > self._month:
                # File is in chronological order so there are no more records
                # for the desired month.
                raise StopIteration
            return record if month == self._month else None

Filters can be chained and are called in order for each record. If any filter
returns None chaining is immediately stopped and the record is dropped. For
the best performance filters should be ordered from most restrictive (most
likely to return None) to least.

    reader.filter(MonthFilter(3))
    reader.filter(LocalTime())
    for record in reader:
        """ All records in March with timestamp converted to CST. """
        print(record)



## Writing Data ##

Writing data to a stream is (mostly) symmetric to reading. Writers use the same
field definitions as Readers with some additional requirements. A data type can
be initialized with a [format string][2]; this is ignored by Readers, but it is
used by Writers to convert a Python value to text. Each data type has a default
format, but for `FixedWidthWriter` fields a format string with the appropriate
field width (inclusive of spaces between fields) **must** be specified.

For the `FixedWidthReader` example the time zone field was ignored. However,
when defining fields for a `FixedWidthWriter`, every field must be defined,
even if it's blank. Also, fields must be listed in their correct order.

A Writer expects a value to write for each of its fields for every data record
to be written. If a field is missing from an output record the Writer will use 
the default value for that field (None is encoded as a blank field). Fields in 
the record that do not correspond to an output field are ignored.

Filters work for Writers like they do for Readers. The filters defined for a
Writer are applied to each record passed to the write() method before the
record is written to the stream. If any filter return None the record is not
written.

With some minor modifications the field definitions for reading the sample
data can be used for writing it. In fact, the modified fields can still be used
for reading the data, so a Reader and a Writer can be defined for a given data
format using one set of field definitions.

    data_fields = (
        ("value", (0, 8), FloatType("8.2f")),  # don't forget leading space
        ("flag", (8, 9), StringType("1s")))

    sample_fields = (
        ("stid", (0, 6), StringType("6s")),
        ("timestamp", (6, 23), DatetimeType("%Y-%m-%d %H:%M:%S")),
        ("timezone", (23, 27), StringType(">4s", default="UTC")),
        ("data", (27, None), ArrayType(data_fields)))  # no format string

    with open("data.txt", "r") as istream, open("copy.txt", "w") as ostream:
        # Copy "data.txt" to "copy.txt".
        reader = FixedWidthReader(istream, sample_fields)
        writer = FixedWidthWriter(ostream, sample_fields)
        for record in reader:
            record.pop("timezone")  # rely on default value
            writer.write(record)


## Delimited Data ##

The `DelimitedReader` and `DelimitedWriter` classes can be used for reading and
writing delimited data, e.g. CSV values:

    340010,2012-02-01 00:00,UTC,-999.00,M,-999.00,S
    340010,2012-03-01 00:00,UTC,72.00,,1.23,A
    340010,2012-04-01 00:10,UTC,63.80,Q,0.00,

Delimited fields are defined in the same way as fixed-width fields except that
the field positions are given by index number instead of character positions.
Scalar field positions are a single number while array field positions are a
[begin, end) pair. The format string is optional for most field types because a
width is not required.

    from serial.core import DelimiteReader
    from serial.core import DelimiteWriter

    data_fields = (
        ("value", 0, FloatType(".2f")),  # don't need width
        ("flag", 1, StringType()))  # default format

    sample_fields = (
        ("stid", 0, StringType()),  # default format
        ("timestamp", 1, DatetimeType("%Y-%m-%d %H:%M:%S")),  # format required
        ("timezone", 2, StringType(default="UTC")),  # default format
        ("data", (3, None), ArrayType(data_fields)))  # variable length

    delim = ","
    reader = DelimitedReader(istream, sample_fields, delim)
    writer = DelimitedWriter(ostream, sample_fields, delim)


## Extending Core Classes ##

All the field definitions and filters for a specific format can be encapsulated
in a class that inherits from the appropriate Reader or Writer, and these
classes can be bundled into a module for that format.

    """ Module for reading and writing the sample data format.

    Timestamps are converted from/to UTC to/from LST in the data stream.

    """
    ...
    from serial.core import ConstType

    _DATA_FIELDS = (
      ("value", 0, FloatType(".2f")),
      ("flag", 1, StringType()))

    _SAMPLE_FIELDS = (
      ("stid", 0, StringType()),
      ("timestamp", 1, DatetimeType("%Y-%m-%d %H:%M:%S")),
      ("timezone", 2, ConstType("UTC")),  # constant-valued field
      ("data", (3, None), ArrayType(data_fields)))

    class SampleReader(DelimitedReader):
        """ Sample data reader.

        Base class implements iterator protocol for reading records.

        """
        def __init__(self, offset=-6):
            super(SampleReader, self).__init__(_SAMPLE_FIELDS, _DELIM)
            self._offset = timedelta(hours=offset)  # offset from UTC
            self.filter(self._timstamp_filter)
            return

        def _timestamp_filter(self, record):
            """ Filter function for LST corrections. """
            record["timestamp"] += self._offset  # UTC to LST
            record["timezone"] = "LST"
            return

    class SampleWriter(DelimitedWriter):
        """ Sample data writer.

        Base class defines write() for writing records.

        """
        def __init__(self, offset=-6):
            super(SampleWriter, self).__init__(_SAMPLE_FIELDS, _DELIM)
            self._offset = timedelta(hours=offset)  # offset from UTC
            self.filter(self._timestamp_filter)
            return

        def _timestamp_filter(self, record):
            """ Filter function for UTC corrections. """
            record["timestamp"] -= self._offset  # LST to UTC
            record["timezone"] = "UTC"
            return


## Stream Adaptors ##

Readers and Writers are both initialized with stream arguments. A Reader's
input stream is any object that implements a `next()` method that return the
record from the stream as a single line of text. A Writer's output stream is
any object that implements a `write()` method to write a line of text. A Python
`file` object satisfies the requirements for both types of streams. The
`IStreamAdaptor` and `OStreamAdaptor` abstract classes declare the required
interfaces and can be used to create adaptors for other types of streams,
*e.g.* binary data.

    from serial.core import IStreamAdaptor
    from serial.core import OStreamAdaptor

    class BinaryStream(IStreamAdaptor, OStreamAdaptor):
        """ Interface for a binary data stream.

        This can be used to initialize a serial Reader or Writer.

        """
        ...

        def next(self):
            """ IStreamAdaptor: Return the next record as a line of text. """
            # Read the next record from the stream and convert to text.
            return line

        def write(self, line):
            """ OStreamAdaptor: Write a line of text to the stream. """
            # Convert line of text to binary data and write to stream.
            return


## Tips and Tricks ##

### Header Data ###

Header data is outside the scope of `serial.core`. Client code is responsible
for reading or writing header data from or to the stream before `next()` or
`write()` is called for the first time. For derived classes this is typically
done by the `__init__()` method.

The `IStreamBuffer` class is a stream adaptor that adds buffering to input
streams. This is useful for parsing streams where the end of the header data
can only be identified by encountering the first data record.

    from serial.core import DelimitedReader
    from serial.core import IStreamBuffer

    class DataReader(DelimitedReader):
        """ Read data that has header information. """
        ...

        def __init__(self, stream):
            # Header information can be read before or afer the base class is
            # initialized, but it must be done before next() is called.
            stream = IStreamBuffer(stream)
            while not is_data(stream.next()):
                # Parse header. At the end of the loop the first data record
                # has already been read.
                ...
            stream.rewind()  # reposition at first data record
            super(DataReader, self).__init__(stream, _FIELDS, _DELIM)
            return


### Mixed-Type Data ###

Mixed-type data fields must be defined as a `StringType` for stream input and
output, but filters can be used to convert to/from multiple Python types based
on the field value.

    def missing_filter(record):
        """ Input filter for numeric data that's 'M' if missing. """
        try:
            record["data"] = float(record["mixed"])
        except ValueError:  # conversion failed, value is 'M'
            record["data"] = None  # a more convient value for missing data
        return record


### Combined Fields ###

Filters can be used to map a single field in the input/output stream to/from
multiple fields in the data record, or *vice versa*.

    def timestamp_filter(record):
        """ Output filter to split "timestamp" into separate fields. """
        # The data format defines separate "date" and "time" fields instaad of
        # the combined "timestamp". The superfluous timestamp field will be
        # ignored by the Writer so deleting it is redundant.
        record = record.copy()  # write() shouldn't have any side effects
        record["date"] = record["timestamp"].date()
        record["time"] = record["timestamp"].time()
        return record

<!-- REFERENCES -->
[1]: http://docs.python.org/2/library/datetime.html#strftime-strptime-behavior "datetime documentation"
[2]: http://docs.python.org/2/library/string.html#formatspec "format strings"