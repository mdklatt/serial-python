###########
serial-core
###########

|python3.8|
|python3.9|
|python3.10|
|python3.11|
|release|
|license|
|tests|

The *serial-python* Python library provides extensible tools for reading and
writing record-oriented data in various formats. The core library provided here
is contained in the ``serial.core`` package. Library extensions will be
contained in their own packages under the ``serial`` namespace.


========
Features
========

- Read/write delimited and fixed-width data
- Named, typed, and formatted data fields
- Filtering
- Aggregation
- Sorting


=============
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
        IntField("age", 1)
    )
    with DelimitedReader.open("ages.csv", fields, ",") as reader:
        reader.filter(name_filter)
        for record in reader:
            print("{name} is {age} years old".format(**record))


============
Installation
============

Install the library from `GitHub`_:

.. code-block:: console

    $ python -m pip install git+git://github.com/mdklatt/serial-python.git


.. |python3.8| image:: https://img.shields.io/static/v1?label=python&message=3.8&color=informational
    :alt: Python 3.8
.. |python3.9| image:: https://img.shields.io/static/v1?label=python&message=3.9&color=informational
    :alt: Python 3.9
.. |python3.10| image:: https://img.shields.io/static/v1?label=python&message=3.10&color=informational
    :alt: Python 3.10
.. |python3.11| image:: https://img.shields.io/static/v1?label=python&message=3.11&color=informational
    :alt: Python 3.11
.. |release| image:: https://img.shields.io/github/v/release/mdklatt/serial-python?sort=semver
    :alt: GitHub release (latest SemVer)
.. |license| image:: https://img.shields.io/github/license/mdklatt/serial-python
    :alt: MIT License
    :target: `MIT License`_
.. |tests| image:: https://github.com/mdklatt/serial-python/actions/workflows/tests.yml/badge.svg
    :alt: CI Tests
    :target: `GitHub Actions`_


.. _GitHub: https://github.com/mdklatt/serial-python
.. _MIT License: https://choosealicense.com/licenses/mit
.. _GitHub Actions: https://github.com/mdklatt/httpexec/actions/workflows/tests.yml
