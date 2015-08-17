""" Common test fixtures.

"""
import pytest


@pytest.fixture
def writer():
    """ Return a mock writer for testing.

    """
    class _MockWriter(object):
        """ Simulate a _Writer for testing purposes.

        """
        def __init__(self):
            """ Initialize this object.

            """
            self.output = []
            self.write = self.output.append
            return

    return _MockWriter()
