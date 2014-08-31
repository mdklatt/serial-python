""" Master test script.

"""
from os.path import dirname
from os.path import join

import _unittest as unittest

def main():
    """ Run all tests in this directory.

    The test directory is searched for all test scripts ('test_*.py'), and all
    the unit tests (TestCase implementations) they contain are run as a single
    test suite.
    
    """
    path = join(dirname(__file__))
    suite = unittest.defaultTestLoader.discover(path, "*_test.py")
    result = unittest.TextTestRunner().run(suite)
    return 0 if result.wasSuccessful() else 1


# Make the script executable.

if __name__ == "__main__":
    raise SystemExit(main())
