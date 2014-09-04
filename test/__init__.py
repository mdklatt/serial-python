""" The serial.core library test package.

Tests must be run from the project root directory. Use `python setup.py test`
to run the entire test suite or `python -m test.name` to run individual
tests.

"""
from os.path import join
from os.path import dirname
from sys import modules
from sys import path


# Add the project root to the path so that the development version of the 
# library is always loaded.

path.insert(0, join(dirname(__file__), ".."))


# If unittest2 is installed (i.e. for Python 2.6) alias it so that test modules
# don't know the difference.

try:
    import unittest2
    modules["unittest"] = unittest2
except ImportError:
    pass

