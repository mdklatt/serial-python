serial-python
=============

Overview
--------
[![status][1]][2]

The [`serial`][3] library provides Python tools for reading and writing record-
oriented data in various formats. The core library is contained in the
`serial.core` package. Library extensions are contained in their own packages.


Requirements
------------
* Python 2.6 - 2.7
* [unittest2][4] (optional; required to run tests with Python 2.6)

Requirements can be installed using `pip`:

    pip install -r optional-requirements.txt


Installation
------------
Place the [serial][5] directory in the Python [module search path][6]. The 
[setup script][7] can be used to install the library in the desired location,
typically the system or user-specific `site-packages` directory.

    python setup.py install --user  # install for the current user


Usage
-----
The core package requires a single import.

    import serial.core
     
The [tutorial][8] has examples of how to use and extend this library.



<!-- REFERENCES -->
[1]: https://travis-ci.org/mdklatt/serial-python.png?branch=master "Travis build status"
[2]: https://travis-ci.org/mdklatt/serial-python "Travis-CI"
[3]: http://github.com/mdklatt/serial-python "GitHub/serial"
[4]: http://pypi.python.org/pypi/unittest2 "unittest2"
[5]: http://github.com/mdklatt/serial-python/tree/master/serial "serial tree"
[6]: http://docs.python.org/tutorial/modules.html#the-module-search-path "Python import"
[7]: https://github.com/mdklatt/serial-python/blob/master/setup.py "setup.py"
[8]: http://github.com/mdklatt/serial-python/blob/master/doc/tutorial.md "tutorial.md"
