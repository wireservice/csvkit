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
                  [-p` ESCAPECHAR] [-e ENCODING] [-f FORMAT] [-s SCHEMA]
                  [FILE]

    Convert common, but less awesome, tabular data formats to CSV.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      -f FORMAT, --format FORMAT
                            The format of the input file. If not specified will be
                            inferred from the filename. Supported formats: csv,
                            fixed, json, xls, xlsx.
      -s SCHEMA, --schema SCHEMA
                            Specifies a CSV-formatted schema file for converting
                            fixed-width files. See documentation for details.
      -k KEY, --key KEY     Specifies a top-level key to use look within for a
                            list of objects to be converted when processing JSON.
      -y SNIFFLIMIT, --snifflimit SNIFFLIMIT
                            Limit CSV dialect sniffing to the specified number of
                            bytes.

Also see: :doc:`common_arguments`.

Examples
========

Convert the 2000 census geo headers file from fixed-width to CSV and from latin-1 encoding to utf8::

    $ in2csv -e iso-8859-1 -f fixed -s examples/realdata/census_2000/census2000_geo_schema.csv examples/realdata/census_2000/usgeo_excerpt.upl > usgeo.csv

Convert an Excel .xls file::

    $ in2csv examples/test.xls

Standardize the formatting of a CSV file (quoting, line endings, etc.)::

    $ in2csv examples/realdata/FY09_EDU_Recipients_by_State.csv

Fetch csvkit's open issues from the Github API, convert the JSON response into a CSV, and write it to a file::

    $ curl http://github.com/api/v2/json/issues/list/onyxfish/csvkit/open | in2csv -v -k issues > issues.csv 

