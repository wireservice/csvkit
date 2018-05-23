.. image:: https://secure.travis-ci.org/wireservice/csvkit.svg
    :target: https://travis-ci.org/wireservice/csvkit
    :alt: Build Status

.. image:: https://coveralls.io/repos/wireservice/csvkit/badge.svg?branch=master
    :target: https://coveralls.io/r/wireservice/csvkit
    :alt: Coverage Status

.. image:: https://img.shields.io/pypi/v/csvkit.svg
    :target: https://pypi.python.org/pypi/csvkit
    :alt: Version

.. image:: https://img.shields.io/pypi/l/csvkit.svg
    :target: https://pypi.python.org/pypi/csvkit
    :alt: License

.. image:: https://img.shields.io/pypi/pyversions/csvkit.svg
    :target: https://pypi.python.org/pypi/csvkit
    :alt: Support Python versions

csvkit is a suite of command-line tools for converting to and working with CSV, the king of tabular file formats.

It is inspired by pdftk, GDAL and the original csvcut tool by Joe Germuska and Aaron Bycoffe.

.. note::

    If you need to do more complex data analysis than csvkit can handle, use `agate <https://github.com/wireservice/agate>`_.

.. note::

    Remember that to change the field separator, line terminator, etc. of the **output**, you must use :doc:`/scripts/csvformat`.

.. note::

    csvkit, by default, `sniffs <https://docs.python.org/3.5/library/csv.html#csv.Sniffer>`_ CSV formats (it deduces whether commas, tabs or spaces delimit fields, for example), and performs type inference (it converts text to numbers, dates, booleans, etc.). These features are useful and work well in most cases, but occasional errors occur. If you don't need these features, set :code:`--snifflimit 0` (:code:`-y 0`) and :code:`--no-inference` (:code:`-I`).

.. note::

    If you need csvkit to be faster or to handle larger files, you may be reaching the limits of csvkit.

Important links:

* Documentation: http://csvkit.rtfd.org/
* Repository:    https://github.com/wireservice/csvkit
* Issues:        https://github.com/wireservice/csvkit/issues
* Schemas:       https://github.com/wireservice/ffs
