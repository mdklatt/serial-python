""" The library test package.

Use `python -m test` to run the entire test suite or `python -m test.name` to
run individual test modules from the command line. Import run() to run the test
suite from another script.

"""
from os.path import dirname
from sys import modules
from sys import path
try:
    # If unittest2 is installed (i.e. for Python 2.6) alias it so that test
    # modules don't know the difference.
    import unittest2
    modules["unittest"] = unittest2
except ImportError:
    pass

from .__main__ import main as run

path.insert(0, dirname(dirname(__file__)))  # add project root to path
