======
csvpys
======

Description
===========

Run arbitrary python expression on each CSV row to compute value of a new column.
It is possible to compute many new columns at once using ``-s`` option multiple times::

    usage: csvpys [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
              [-p ESCAPECHAR] [-z MAXFIELDSIZE] [-e ENCODING] [-v] [-l]
              [--zero] [-n] [-s NEW_COLUMN PY_SCRIPT]
              [FILE]

    Python scripting in CSV files. Run arbitrary python expression on each CSV row
    to compute value of a new column.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:

      -n, --names           Display column names and indices from the input CSV
                            and exit.
      -s NEW_COLUMN PY_SCRIPT, --script NEW_COLUMN PY_SCRIPT
                            New column name and a python script.". Inside script
                            use c[0] or ch['header'] locals.

Also see: :doc:`common_arguments`.

Scripting language
==================

There is no custom scripting language. Just use plain python expressions. Internally expressions are evaluated using
python standard ``eval()`` function (they are also precompiled for efficiency). Python expression can use following
locals and globals:

 * Locals references two variables representing current row:
    * ``c`` - list of column values indexed with column id (default: 1-based indexing, with ``--zero`` enabled indexing is 0-based),
    * ``ch`` - dict with values accessible via columns name.
 * Globals are supplied with following modules:
    * re and `Rex <https://github.com/cypreess/python-rex>`_ (rex is regular expressions for humans, specially written by experiences using csvkit scripting),
    * math,
    * random,
    * collections.

.. note::

    Remember that both ``c`` and ``ch`` variables have unicode type. Need to be converted if used in other contexts
    than strings.


Examples
========

For following data::

    $ csvcut -c 1,4,5 examples/realdata/FY09_EDU_Recipients_by_State.csv | csvlook
    |--------------------+--------------------------------+----------------------------------------|
    |  State Name        | Montgomery GI Bill-Active Duty | Montgomery GI Bill- Selective Reserve  |
    |--------------------+--------------------------------+----------------------------------------|
    |  ALABAMA           | 6,718                          | 1,728                                  |
    |  ALASKA            | 776                            | 154                                    |
    |  ARIZONA           | 26,822                         | 2,005                                  |
    |  ARKANSAS          | 2,061                          | 988                                    |
    |  CALIFORNIA        | 34,942                         | 2,987                                  |
    |  COLORADO          | 10,389                         | 914                                    |
    |  CONNECTICUT       | 1,771                          | 490                                    |

        ...                ...                              ...

    |  WYOMING           | 686                            | 212                                    |
    |  PUERTO RICO       | 822                            | 1,107                                  |
    |                    |                                |                                        |
    |--------------------+--------------------------------+----------------------------------------|


Let's sum values for both Montgomery GI Bill::

    $ csvcut -c 1,4,5 examples/realdata/FY09_EDU_Recipients_by_State.csv | csvpys -s TOTAL "int(c[2].replace(',', '') if c[2] != '' else 0) + int(c[3].replace(',', '') if c[3] != '' else 0)" | csvlook
    |--------------------+--------------------------------+---------------------------------------+--------|
    |  State Name        | Montgomery GI Bill-Active Duty | Montgomery GI Bill- Selective Reserve | TOTAL  |
    |--------------------+--------------------------------+---------------------------------------+--------|
    |  ALABAMA           | 6,718                          | 1,728                                 | 8446   |
    |  ALASKA            | 776                            | 154                                   | 930    |
    |  ARIZONA           | 26,822                         | 2,005                                 | 28827  |
    |  ARKANSAS          | 2,061                          | 988                                   | 3049   |
    |  CALIFORNIA        | 34,942                         | 2,987                                 | 37929  |
    |  COLORADO          | 10,389                         | 914                                   | 11303  |
    |  CONNECTICUT       | 1,771                          | 490                                   | 2261   |

        ...                ...                              ...

    |  WYOMING           | 686                            | 212                                   | 898    |
    |  PUERTO RICO       | 822                            | 1,107                                 | 1929   |
    |                    |                                |                                       | 0      |
    |--------------------+--------------------------------+---------------------------------------+--------|




.. note::

    Expression ``int(c[2].replace(',', '') if c[2] != '' else 0)`` converts a string e.g. ``"4,156"`` or empty string to a proper int value (``4156``), by removing semicolon and casting to int or returning 0 on empty string.



The same using column names::

    $ csvcut -c 1,4,5 examples/realdata/FY09_EDU_Recipients_by_State.csv | csvpys -s TOTAL "int(ch['Montgomery GI Bill-Active Duty'].replace(',', '') if ch['Montgomery GI Bill-Active Duty'] != '' else 0) + int(ch['Montgomery GI Bill- Selective Reserve'].replace(',', '') if ch['Montgomery GI Bill- Selective Reserve'] != '' else 0)" | csvlook



Other example, let's play with data::

    $ csvcut -c 1,8 examples/realdata/FY09_EDU_Recipients_by_State.csv | csvlook
    |--------------------+------------------------------------------------------------|
    |  State Name        | Post-Vietnam Era Veteran's Educational Assistance Program  |
    |--------------------+------------------------------------------------------------|
    |  ALABAMA           | 8                                                          |
    |  ALASKA            | 2                                                          |
    |  ARIZONA           | 11                                                         |
    |  ARKANSAS          | 3                                                          |
    |  CALIFORNIA        | 48                                                         |
    |  COLORADO          | 10                                                         |
    |  CONNECTICUT       | 4                                                          |

        ...                ...

    |  WYOMING           | 1                                                          |
    |  PUERTO RICO       | 3                                                          |
    |                    |                                                            |
    |--------------------+------------------------------------------------------------|

The task is to classify as True all states that have a value greater or equal than 10 in second column::

    $ csvcut -c 1,8 examples/realdata/FY09_EDU_Recipients_by_State.csv | csvpys -s Classify "bool(int(c[2])>=10) if c[2] != '' else ''" | csvlook
    |--------------------+-----------------------------------------------------------+-----------|
    |  State Name        | Post-Vietnam Era Veteran's Educational Assistance Program | Classify  |
    |--------------------+-----------------------------------------------------------+-----------|
    |  ALABAMA           | 8                                                         | False     |
    |  ALASKA            | 2                                                         | False     |
    |  ARIZONA           | 11                                                        | True      |
    |  ARKANSAS          | 3                                                         | False     |
    |  CALIFORNIA        | 48                                                        | True      |
    |  COLORADO          | 10                                                        | True      |
    |  CONNECTICUT       | 4                                                         | False     |

        ...                ...                                                          ...

    |  WYOMING           | 1                                                         | False     |
    |  PUERTO RICO       | 3                                                         | False     |
    |                    |                                                           |           |
    |--------------------+-----------------------------------------------------------+-----------|

.. note::

    If statement is only needed because we need to deal with last line which has empty string ``''``.


OK, within the last example we will calculate number of A's in state names::

    $ csvcut -c 1 examples/realdata/FY09_EDU_Recipients_by_State.csv | csvpys -s "A letter count" "collections.Counter(c[1])['A']" | csvlook
    |--------------------+-----------------|
    |  State Name        | A letter count  |
    |--------------------+-----------------|
    |  ALABAMA           | 4               |
    |  ALASKA            | 3               |
    |  ARIZONA           | 2               |
    |  ARKANSAS          | 3               |
    |  CALIFORNIA        | 2               |
    |  COLORADO          | 1               |
    |  CONNECTICUT       | 0               |

        ...                 ...

    |  WYOMING           | 0               |
    |  PUERTO RICO       | 0               |
    |                    | 0               |
    |--------------------+-----------------|


Regular expressions can also be very useful in scripting. You can use very simple module named Rex, because
standard python re implementation is not very continence to use in online expressions. For more information on `Rex please
refer to documentation <https://github.com/cypreess/python-rex>`_.

Let's use already nice regular expressions support of csvkit, and grep columns to leave only states with started with "NEW"::

    $ csvcut -c 1-3 examples/realdata/FY09_EDU_Recipients_by_State.csv | csvgrep -c 1 -r "^NEW" | csvlook
    |----------------+------------------+-------|
    |  State Name    | State Abbreviate | Code  |
    |----------------+------------------+-------|
    |  NEW HAMPSHIRE | NH               | 33    |
    |  NEW JERSEY    | NJ               | 34    |
    |  NEW MEXICO    | NM               | 35    |
    |  NEW YORK      | NY               | 36    |
    |----------------+------------------+-------|



Let's say we would like to extract the second part of the state name and concatenate it with the state abbreviate (e.g. for ``NEW YORK`` => ``YORK (NY)``). Of course it could be done in plenty of ways, but we would like to use regular expressions for that::

    $ csvcut -c 1-3 examples/realdata/FY09_EDU_Recipients_by_State.csv | csvgrep -c 1 -r "^NEW" | csvpys -s "New name" "(c[1] == rex('/^new (.*)$/i'))[1] + ' (' + c[2] + ')'" | csvlook
    |----------------+------------------+------+-----------------|
    |  State Name    | State Abbreviate | Code | New name        |
    |----------------+------------------+------+-----------------|
    |  NEW HAMPSHIRE | NH               | 33   | HAMPSHIRE (NH)  |
    |  NEW JERSEY    | NJ               | 34   | JERSEY (NJ)     |
    |  NEW MEXICO    | NM               | 35   | MEXICO (NM)     |
    |  NEW YORK      | NY               | 36   | YORK (NY)       |
    |----------------+------------------+------+-----------------|


Yes, it's that simple and powerful!