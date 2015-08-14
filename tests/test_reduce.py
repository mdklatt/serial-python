""" Testing for the the reduce.py module

The script can be executed on its own or incorporated into a larger test suite.
However the tests are run, be aware of which version of the module is actually
being tested. If the library is installed in site-packages, that version takes
precedence over the version in this project directory. Use a virtualenv test
environment or setuptools develop mode to test against the development version.

"""
import pytest

from fixture import writer
from serial.core.reduce import *  # tests __all__


@pytest.fixture
def input():
    return [
        {"str": "abc", "int": 1, "float": 1.},
        {"str": "abc", "int": 1, "float": 2.},
        {"str": "abc", "int": 3, "float": 3.},
        {"str": "def", "int": 3, "float": 4.},
    ]


class AggregateReaderTest(object):
    """ Unit testing for the AggregateReader class.

    """
    def test_reduction(self, input):
        """ Test the reduction() class method.

        """
        add = lambda args: sum(a + b for a, b in args)
        reduction = AggregateReader.reduction(add, ("int", "float"), "sum")
        assert reduction(input) == {"sum": 18}
        return

    def test_iter(self, input):
        """ Test the iterator protocol.

        """
        reader = iter(input)
        aggregator = AggregateReader(reader, "str")
        aggregator.reduce(
            AggregateReader.reduction(sum, "int"),
            AggregateReader.reduction(max, "float"),
        )
        output = (
            {"str": "abc", "int": 5, "float": 3.},
            {"str": "def", "int": 3, "float": 4.},
        )
        assert tuple(aggregator) == output
        return

    def test_iter_multi(self, input):
        """ Test the iterator protocol with multi-key grouping.

        """
        reader = iter(input)
        aggregator = AggregateReader(reader, ("str", "int"))
        aggregator.reduce(AggregateReader.reduction(max, "float"))
        output = (
            {"str": "abc", "int": 1, "float": 2.},
            {"str": "abc", "int": 3, "float": 3.},
            {"str": "def", "int": 3, "float": 4.}
        )
        assert tuple(aggregator) == output
        return

    def test_iter_custom(self, input):
        """ Test the iterator protocol with a custom key function.

        """
        reader = iter(input)
        key = lambda record: {"KEY": record["str"].upper()}
        aggregator = AggregateReader(reader, key)
        aggregator.reduce(AggregateReader.reduction(sum, "int"))
        aggregator.reduce(AggregateReader.reduction(max, "float"))
        output = (
            {"KEY": "ABC", "int": 5, "float": 3.},
            {"KEY": "DEF", "int": 3, "float": 4.},
        )
        assert tuple(aggregator) == output
        return


class AggregateWriterTest(object):
    """ Unit testing for the AggregateWriter class.

    """
    def test_reduction(self, input):
        """ Test the reduction() class method.

        """
        add = lambda args: sum(a + b for a, b in args)
        reduction = AggregateWriter.reduction(add, ("int", "float"), "sum")
        assert reduction(input) == {"sum": 18}
        return

    def test_write(self, input, writer):
        """ Test the write() and close() methods.

        """
        aggregator = AggregateWriter(writer, "str")
        aggregator.reduce(
            AggregateWriter.reduction(sum, "int"),
            AggregateWriter.reduction(max, "float")
        )
        for record in input:
            aggregator.write(record)
        aggregator.close()
        aggregator.close()  # test that redundant calls are a no-op
        output = (
            {"str": "abc", "int": 5, "float": 3.},
            {"str": "def", "int": 3, "float": 4.},
        )
        assert tuple(writer.output) == output
        return

    def test_write_multi(self, input, writer):
        """ Test the write() method with a multi-field key.

        """
        aggregator = AggregateWriter(writer, ("str", "int"))
        aggregator.reduce(AggregateWriter.reduction(max, "float"))
        for record in input:
            aggregator.write(record)
        aggregator.close()
        output = (
            {"str": "abc", "int": 1, "float": 2.},
            {"str": "abc", "int": 3, "float": 3.},
            {"str": "def", "int": 3, "float": 4.},
        )
        assert tuple(writer.output) == output
        return

    def test_write_custom(self, input, writer):
        """ Test the write() method with a custom key function.

        """
        key = lambda record: {"KEY": record["str"].upper()}
        aggregator = AggregateWriter(writer, key)
        aggregator.reduce(AggregateWriter.reduction(max, "float"))
        for record in input:
            aggregator.write(record)
        aggregator.close()
        output = (
            {"KEY": "ABC", "float": 3.},
            {"KEY": "DEF", "float": 4.},
        )
        assert tuple(writer.output) == output
        return

    def test_dump(self, input, writer):
        """ Test the dump() method.

        """
        aggregator = AggregateWriter(writer, "str")
        aggregator.reduce(
            AggregateWriter.reduction(sum, "int"),
            AggregateWriter.reduction(max, "float")
        )
        aggregator.dump(input)
        output = (
            {"str": "abc", "int": 5, "float": 3.},
            {"str": "def", "int": 3, "float": 4.},
        )
        assert tuple(writer.output) == output
        return


# Make the module executable.

if __name__ == "__main__":
    raise SystemExit(pytest.main(__file__))
