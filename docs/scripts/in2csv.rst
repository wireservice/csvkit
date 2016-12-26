======
in2csv
======

Description
===========

Converts various tabular data formats into CSV.

Converting fixed width requires that you provide a schema file with the "-s" option. The schema file should have the following format::

    column,start,length
    name,0,30
    birthday,30,10
    age,40,3

The header line is required though the columns may be in any order::

    usage: in2csv [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                  [-p ESCAPECHAR] [-z MAXFIELDSIZE] [-e ENCODING] [-S] [-H] [-v]
                  [-l] [--zero] [-f FILETYPE] [-s SCHEMA] [-k KEY] [-y SNIFFLIMIT]
                  [--sheet SHEET] [--no-inference]
                  [FILE]

    Convert common, but less awesome, tabular data formats to CSV.

    positional arguments:
      FILE                  The file to operate on. If omitted, will accept input
                            on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      -f FILETYPE, --format FILETYPE
                            The format of the input file. If not specified will be
                            inferred from the file type. Supported formats: csv,
                            fixed, geojson, json, ndjson, xls, xlsx.
      -s SCHEMA, --schema SCHEMA
                            Specifies a CSV-formatted schema file for converting
                            fixed-width files. See documentation for details.
      -k KEY, --key KEY     Specifies a top-level key to use look within for a
                            list of objects to be converted when processing JSON.
      -y SNIFFLIMIT, --snifflimit SNIFFLIMIT
                            Limit CSV dialect sniffing to the specified number of
                            bytes. Specify "0" to disable sniffing entirely.
      --sheet SHEET         The name of the XLSX sheet to operate on.
      --no-inference        Disable type inference when parsing the input.

See also: :doc:`../common_arguments`.

.. note::

    The "ndjson" format refers to "newline delimited JSON", as used by many streaming APIs.

.. note::

    If an XLS looks identical to an XLSX when viewed in Excel, they may not be identical as CSV. For example, XLSX has an integer type, but XLS doesn't. Numbers that look like integers from an XLS will have decimals in CSV, but those from an XLSX won't.

.. note::

    To convert from HTML, consider `messytables <https://messytables.readthedocs.io/>`_.

Examples
========

Convert the 2000 census geo headers file from fixed-width to CSV and from latin-1 encoding to utf8::

    in2csv -e iso-8859-1 -f fixed -s examples/realdata/census_2000/census2000_geo_schema.csv examples/realdata/census_2000/usgeo_excerpt.upl

.. note::

    A library of fixed-width schemas is maintained in the ``ffs`` project:

    https://github.com/wireservice/ffs

Convert an Excel .xls file::

    in2csv examples/test.xls

Standardize the formatting of a CSV file (quoting, line endings, etc.)::

    in2csv examples/realdata/FY09_EDU_Recipients_by_State.csv

Fetch csvkit's open issues from the GitHub API, convert the JSON response into a CSV and write it to a file::

    curl https://api.github.com/repos/wireservice/csvkit/issues?state=open | in2csv -f json -v

Convert a DBase DBF file to an equivalent CSV::

    in2csv examples/testdbf.dbf
