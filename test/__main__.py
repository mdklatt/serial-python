""" Run the test suite.

    python -m test
    python -m test.__main__  # Python 2.6

"""
from os.path import dirname
from unittest import defaultTestLoader
from unittest import TextTestRunner


def main():
    """ Run all tests in this directory.

    """
    suite = defaultTestLoader.discover(dirname(__file__), "[a-z]*.py")
    result = TextTestRunner().run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    # Called from command line.
    raise SystemExit(main())
