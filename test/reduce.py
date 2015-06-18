""" Testing for the the reduce.py module

The module can be executed on its own or incorporated into a larger test suite.

"""
import unittest

from serial.core.reduce import *  # tests __all__


# Mock objects to use for testing.

class _MockWriter(object):
    """ Simulate a _Writer for testing purposes.
    
    """
    def __init__(self):
        """ Initialize this object.
        
        """
        self.output = []
        self.write = self.output.append
        return


# Define the TestCase classes for this module. Each public component of the
# module being tested has its own TestCase.


class _AggregateTest(object):
    """ Abstract base class for AggregateReader/Writer class unit testing.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        self.records = (
            {"str": "abc", "int": 1, "float": 1.},
            {"str": "abc", "int": 1, "float": 2.},
            {"str": "abc", "int": 3, "float": 3.},
            {"str": "def", "int": 3, "float": 4.})
        return
    

class AggregateReaderTest(_AggregateTest, unittest.TestCase):
    """ Unit testing for the AggregateReader class.

    """
    def test_reduction(self):
        """ Test the reduction() class method.
        
        """
        add = lambda args: sum(a + b for a, b in args)
        reduction = AggregateReader.reduction(add, ("int", "float"), "sum")
        self.assertEqual({"sum": 18}, reduction(self.records))
        return

    def test_iter(self):
        """ Test the iterator protocol.

        """
        reduced = (
            {"str": "abc", "int": 5, "float": 3.},
            {"str": "def", "int": 3, "float": 4.})
        reader = AggregateReader(iter(self.records), "str")
        reader.reduce(AggregateReader.reduction(sum, "int"),
                      AggregateReader.reduction(max, "float"))
        self.assertSequenceEqual(reduced, list(reader))
        return
        
    def test_iter_multi_key(self):
        """ Test the iterator protocol with multi-key grouping.
        
        """
        reduced = (
            {"str": "abc", "int": 1, "float": 2.},
            {"str": "abc", "int": 3, "float": 3.},
            {"str": "def", "int": 3, "float": 4.})
        reader = AggregateReader(iter(self.records), ("str", "int"))        
        reader.reduce(AggregateReader.reduction(max, "float"))        
        self.assertSequenceEqual(reduced, list(reader))
        return

    def test_iter_custom_key(self):
        """ Test the iterator protocol with a custom key function.
        
        """
        reduced = (
            {"KEY": "ABC", "int": 5, "float": 3.},
            {"KEY": "DEF", "int": 3, "float": 4.})
        key = lambda record: {"KEY": record["str"].upper()}
        reader = AggregateReader(iter(self.records), key)
        reader.reduce(AggregateReader.reduction(sum, "int"))
        reader.reduce(AggregateReader.reduction(max, "float"))
        self.assertSequenceEqual(reduced, list(reader))
        return
        

class AggregateWriterTest(_AggregateTest, unittest.TestCase):
    """ Unit testing for the AggregateWriter class.

    """
    def setUp(self):
        """ Set up the test fixture.

        This is called before each test is run so that they are isolated from
        any side effects. This is part of the unittest API.

        """
        super(AggregateWriterTest, self).setUp()
        self.writer = _MockWriter()  
        return

    def test_reduction(self):
        """ Test the reduction() class method.
        
        """
        add = lambda args: sum(a + b for a, b in args)
        reduction = AggregateWriter.reduction(add, ("int", "float"), "sum")
        self.assertEqual({"sum": 18}, reduction(self.records))
        return

    def test_write(self):
        """ Test the write() and close() methods.

        """
        reduced = (
            {"str": "abc", "int": 5, "float": 3.},
            {"str": "def", "int": 3, "float": 4.})
        writer = AggregateWriter(self.writer, "str")
        writer.reduce(
            AggregateWriter.reduction(sum, "int"),
            AggregateWriter.reduction(max, "float"))
        for record in self.records:
            writer.write(record)
        writer.close()
        writer.close()  # test that redundant calls are a no-op
        self.assertSequenceEqual(reduced, self.writer.output)
        return

    def test_write_multi_key(self):
        """ Test the write() method with a multi-field key.

        """
        reduced = (
            {"str": "abc", "int": 1, "float": 2.},
            {"str": "abc", "int": 3, "float": 3.},
            {"str": "def", "int": 3, "float": 4.})
        writer = AggregateWriter(self.writer, ("str", "int"))
        writer.reduce(AggregateWriter.reduction(max, "float"))
        for record in self.records:
            writer.write(record)
        writer.close()
        self.assertSequenceEqual(reduced, self.writer.output)
        return

    def test_write_custom_key(self):
        """ Test the write() method with a custom key function.

        """
        reduced = (
            {"KEY": "ABC", "int": 5, "float": 3.},
            {"KEY": "DEF", "int": 3, "float": 4.})
        key = lambda record: {"KEY": record["str"].upper()}
        writer = AggregateWriter(self.writer, key)
        writer.reduce(
            AggregateWriter.reduction(sum, "int"),
            AggregateWriter.reduction(max, "float"))
        for record in self.records:
            writer.write(record)
        writer.close()
        self.assertSequenceEqual(reduced, self.writer.output)
        return

    def test_dump(self):
        """ Test the dump() method.

        """
        reduced = (
            {"str": "abc", "int": 5, "float": 3.},
            {"str": "def", "int": 3, "float": 4.})
        writer = AggregateWriter(self.writer, "str")
        writer.reduce(
            AggregateWriter.reduction(sum, "int"),
            AggregateWriter.reduction(max, "float"))
        writer.dump(self.records)
        self.assertSequenceEqual(reduced, self.writer.output)
        return


# Make the module executable.

if __name__ == "__main__":
    unittest.main()  # calls sys.exit()
