""" The serial.core library test package.

Tests must be run from the project root directory. Use `python setup.py test`
to run the entire test suite or `python -m tests.xxxx_test` to run individual
tests.

"""
# Add the project root to the path so that the development version of the 
# library is always loaded.

from os.path import join
from os.path import dirname
from sys import path

path.insert(0, join(dirname(__file__), ".."))
