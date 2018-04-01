===========
serial-core
===========
.. |travis.png| image:: https://travis-ci.org/mdklatt/cookiecutter-python-lib.png?branch=master
   :alt: Travis CI build status
   :target: `travis`_
.. _travis: https://travis-ci.org/mdklatt/serial-python
.. _serial: http://github.com/mdklatt/serial-python


|travis.png|

The `serial`_ Python library provides extensible tools for reading and writing
record-oriented data in various formats. The core library provided here is
contained in the ``serial.core`` package. Library extensions will be contained
in their own packages under the ``serial`` namespace.


.. _py27: https://github.com/mdklatt/serial-python/tree/py27

The `py27`_ branch is for Python 2.7 compatibility; it is no longer actively
maintained.


Features
========
- Read/write delimited and fixed-width data
- Named, typed, and formatted data fields
- Filtering
- Aggregation
- Sorting


Basic Example
=============

.. code-block:: python

    """ Read a comma-delimited file.

    """
    from serial.core import DelimitedReader
    from serial.core import IntField
    from serial.core import StringField

    def name_filter(record):
        """ Convert name to upper case. """
        record["name"] = record["name"].upper()
        return record

    fields = (
        StringField("name", 0),
        IntField("age", 1))
    with DelimitedReader.open("ages.csv", fields, ",") as reader:
        reader.filter(name_filter)
        for record in reader:
            print("{name:s} is {age:d} years old".format(**record))


Requirements
============
.. _Sphinx: http://sphinx-doc.org
.. _pytest: http://pytest.org

- `Sphinx`_ (optional; required to build documentation)
- `pytest`_ (optional; required to run test suite)



Installation
============
.. _GitHub: https://github.com/mdklatt/serial-python

Install the library from `GitHub`_:

.. code-block:: shell

    $ python -m pip install git+git://github.com/mdklatt/serial-python.git
