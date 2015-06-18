serial-python
=============

Overview
--------
[![status][1]][2]

The [**serial-python**][3] library provides tools for reading and writing
record-oriented data in various formats. The core library is contained in the
`serial.core` package. Library extensions will be contained in their own 
packages.


Features
--------
* Read/write delimited and fixed-width data
* Named and typed data fields
* Filtering
* Aggregation
* Sorting
* Advanced data transformations 


Requirements
------------
* Python 2.6 - 2.7


Installation
------------
Place the [serial][5] directory in the Python [module search path][6]. The
[setup script][7] can be used to install the library in the desired location,
typically the system or user-specific `site-packages` directory.

    python setup.py install --user


Usage
-----

    import serial.core

The [tutorial][8] has examples of how to use and extend this library.


Testing
-------
Tests are contained in the `test` package and can be run from the package root
on a per-module basis or altogether.

    python -m test.name 
    python -m test           
    python -m test.__main__  # Python 2.6

 
For Python 2.6 the [unittest2][4] library is required to run the test suite.

    pip install --requirement=test/requirements-py26.txt

The test suite can be also run using a [py.test][9] test runner.

    py.test test/



<!-- REFERENCES -->
[1]: https://travis-ci.org/mdklatt/serial-python.png?branch=master "Travis build status"
[2]: https://travis-ci.org/mdklatt/serial-python "Travis-CI"
[3]: http://github.com/mdklatt/serial-python "GitHub/serial"
[4]: http://pypi.python.org/pypi/unittest2 "unittest2"
[5]: http://github.com/mdklatt/serial-python/tree/master/serial "serial tree"
[6]: http://docs.python.org/tutorial/modules.html#the-module-search-path "Python import"
[7]: https://github.com/mdklatt/serial-python/blob/master/setup.py "setup.py"
[8]: http://github.com/mdklatt/serial-python/blob/master/doc/tutorial.md "tutorial.md"
[9]: http://pytest.org/latest "pytest"