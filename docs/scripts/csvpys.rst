=======
csvgrep
=======

Description
===========

Adds one or multiple new column to CSV as a result of python scripts evaluation::

    usage: csvpys [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                  [-p ESCAPECHAR] [-z MAXFIELDSIZE] [-e ENCODING] [-v] [-l]
                  [--zero] [-n] [-s SCRIPT]
                  [FILE]

    Python scripting in CSV files, allowing to save processing result as new csv
    columns.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      -n, --names           Display column names and indices from the input CSV
                            and exit.
      -s SCRIPT, --script SCRIPT
                            New column name and a python script. -c
                            "<NEW_COLUMN_NAME>|<PYTHON SCRIPT>". Inside script use
                            c[0] or ch['header'] locals.

Also see: :doc:`common_arguments`.

Scripting language
==================

There is no custom scripting language. Just use plain python. Locals are supplied with two variables referencing current row:

 * ``c`` - integer indexed variable (by current row's column id; 0-based or 1-based according to ``--zero``)
 option),
 * ``ch`` - string indexed variable (by current row's column name).

Globals are supplied with following modules:

 * ``re``
 * ``math``
 * ``random``
 * ``collections``

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
    |  DELAWARE          | 599                            | 169                                    |
    |  DIST. OF COLUMBIA | 791                            | 48                                     |
    |  FLORIDA           | 26,167                         | 2,678                                  |
    |  GEORGIA           | 11,909                         | 2,128                                  |
    |  HAWAII            | 1,591                          | 377                                    |
    |  IDAHO             | 1,491                          | 545                                    |
    |  ILLINOIS          | 15,659                         | 2,491                                  |
    |  INDIANA           | 4,001                          | 1,757                                  |
    |  IOWA              | 5,694                          | 1,568                                  |
    |  KANSAS            | 2,953                          | 771                                    |
    |  KENTUCKY          | 3,075                          | 1,050                                  |
    |  LOUISIANA         | 3,101                          | 1,360                                  |
    |  MAINE             | 811                            | 274                                    |
    |  MARYLAND          | 7,854                          | 649                                    |
    |  MASSACHUSETTS     | 3,331                          | 872                                    |
    |  MICHIGAN          | 5,254                          | 1,461                                  |
    |  MINNESOTA         | 5,185                          | 1,895                                  |
    |  MISSISSIPPI       | 1,605                          | 1,247                                  |
    |  MISSOURI          | 8,909                          | 1,797                                  |
    |  MONTANA           | 979                            | 338                                    |
    |  NEBRASKA          | 3,145                          | 799                                    |
    |  NEVADA            | 2,647                          | 353                                    |
    |  NEW HAMPSHIRE     | 706                            | 231                                    |
    |  NEW JERSEY        | 3,473                          | 754                                    |
    |  NEW MEXICO        | 2,623                          | 415                                    |
    |  NEW YORK          | 8,795                          | 1,695                                  |
    |  NORTH CAROLINA    | 9,785                          | 1,327                                  |
    |  NORTH DAKOTA      | 679                            | 526                                    |
    |  OHIO              | 7,250                          | 2,673                                  |
    |  OKLAHOMA          | 4,765                          | 1,251                                  |
    |  OREGON            | 3,623                          | 664                                    |
    |  PENNSYLVANIA      | 7,660                          | 2,009                                  |
    |  RHODE ISLAND      | 555                            | 203                                    |
    |  SOUTH CAROLINA    | 3,966                          | 1,343                                  |
    |  SOUTH DAKOTA      | 783                            | 634                                    |
    |  TENNESSEE         | 4,987                          | 1,368                                  |
    |  TEXAS             | 27,894                         | 3,101                                  |
    |  UTAH              | 2,811                          | 1,106                                  |
    |  VERMONT           | 435                            | 120                                    |
    |  VIRGINIA          | 15,030                         | 1,358                                  |
    |  WASHINGTON        | 7,969                          | 769                                    |
    |  WEST VIRGINIA     | 6,040                          | 896                                    |
    |  WISCONSIN         | 4,156                          | 1,547                                  |
    |  WYOMING           | 686                            | 212                                    |
    |  PUERTO RICO       | 822                            | 1,107                                  |
    |                    |                                |                                        |
    |--------------------+--------------------------------+----------------------------------------|


Lets sum values for both Montgomery GI Bill::

    $ csvcut -c 1,4,5 examples/realdata/FY09_EDU_Recipients_by_State.csv | csvpys -s "TOTAL|int(c[2].replace(',', '') if c[2] != '' else 0) + int(c[3].replace(',', '') if c[3] != '' else 0)" | csvlook
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
    |  DELAWARE          | 599                            | 169                                   | 768    |
    |  DIST. OF COLUMBIA | 791                            | 48                                    | 839    |
    |  FLORIDA           | 26,167                         | 2,678                                 | 28845  |
    |  GEORGIA           | 11,909                         | 2,128                                 | 14037  |
    |  HAWAII            | 1,591                          | 377                                   | 1968   |
    |  IDAHO             | 1,491                          | 545                                   | 2036   |
    |  ILLINOIS          | 15,659                         | 2,491                                 | 18150  |
    |  INDIANA           | 4,001                          | 1,757                                 | 5758   |
    |  IOWA              | 5,694                          | 1,568                                 | 7262   |
    |  KANSAS            | 2,953                          | 771                                   | 3724   |
    |  KENTUCKY          | 3,075                          | 1,050                                 | 4125   |
    |  LOUISIANA         | 3,101                          | 1,360                                 | 4461   |
    |  MAINE             | 811                            | 274                                   | 1085   |
    |  MARYLAND          | 7,854                          | 649                                   | 8503   |
    |  MASSACHUSETTS     | 3,331                          | 872                                   | 4203   |
    |  MICHIGAN          | 5,254                          | 1,461                                 | 6715   |
    |  MINNESOTA         | 5,185                          | 1,895                                 | 7080   |
    |  MISSISSIPPI       | 1,605                          | 1,247                                 | 2852   |
    |  MISSOURI          | 8,909                          | 1,797                                 | 10706  |
    |  MONTANA           | 979                            | 338                                   | 1317   |
    |  NEBRASKA          | 3,145                          | 799                                   | 3944   |
    |  NEVADA            | 2,647                          | 353                                   | 3000   |
    |  NEW HAMPSHIRE     | 706                            | 231                                   | 937    |
    |  NEW JERSEY        | 3,473                          | 754                                   | 4227   |
    |  NEW MEXICO        | 2,623                          | 415                                   | 3038   |
    |  NEW YORK          | 8,795                          | 1,695                                 | 10490  |
    |  NORTH CAROLINA    | 9,785                          | 1,327                                 | 11112  |
    |  NORTH DAKOTA      | 679                            | 526                                   | 1205   |
    |  OHIO              | 7,250                          | 2,673                                 | 9923   |
    |  OKLAHOMA          | 4,765                          | 1,251                                 | 6016   |
    |  OREGON            | 3,623                          | 664                                   | 4287   |
    |  PENNSYLVANIA      | 7,660                          | 2,009                                 | 9669   |
    |  RHODE ISLAND      | 555                            | 203                                   | 758    |
    |  SOUTH CAROLINA    | 3,966                          | 1,343                                 | 5309   |
    |  SOUTH DAKOTA      | 783                            | 634                                   | 1417   |
    |  TENNESSEE         | 4,987                          | 1,368                                 | 6355   |
    |  TEXAS             | 27,894                         | 3,101                                 | 30995  |
    |  UTAH              | 2,811                          | 1,106                                 | 3917   |
    |  VERMONT           | 435                            | 120                                   | 555    |
    |  VIRGINIA          | 15,030                         | 1,358                                 | 16388  |
    |  WASHINGTON        | 7,969                          | 769                                   | 8738   |
    |  WEST VIRGINIA     | 6,040                          | 896                                   | 6936   |
    |  WISCONSIN         | 4,156                          | 1,547                                 | 5703   |
    |  WYOMING           | 686                            | 212                                   | 898    |
    |  PUERTO RICO       | 822                            | 1,107                                 | 1929   |
    |                    |                                |                                       | 0      |
    |--------------------+--------------------------------+---------------------------------------+--------|




.. note::

    Expression ``int(c[2].replace(',', '') if c[2] != '' else 0)`` converts a string e.g. ``"4,156"`` or empty string to a proper int value (``4156``), by removing semicolon and casting to int or returning 0 on empty string.



The same using column names::

    $ csvcut -c 1,4,5 examples/realdata/FY09_EDU_Recipients_by_State.csv | csvpys -s "TOTAL|int(ch['Montgomery GI Bill-Active Duty'].replace(',', '') if ch['Montgomery GI Bill-Active Duty'] != '' else 0) + int(ch['Montgomery GI Bill- Selective Reserve'].replace(',', '') if ch['Montgomery GI Bill- Selective Reserve'] != '' else 0)" | csvlook



Other example, lets play with data::

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
    |  DELAWARE          | 1                                                          |
    |  DIST. OF COLUMBIA | 3                                                          |
    |  FLORIDA           | 28                                                         |
    |  GEORGIA           | 13                                                         |
    |  HAWAII            | 3                                                          |
    |  IDAHO             | 2                                                          |
    |  ILLINOIS          | 19                                                         |
    |  INDIANA           | 8                                                          |
    |  IOWA              | 4                                                          |
    |  KANSAS            | 4                                                          |
    |  KENTUCKY          | 6                                                          |
    |  LOUISIANA         | 4                                                          |
    |  MAINE             | 2                                                          |
    |  MARYLAND          | 13                                                         |
    |  MASSACHUSETTS     | 10                                                         |
    |  MICHIGAN          | 16                                                         |
    |  MINNESOTA         | 10                                                         |
    |  MISSISSIPPI       | 3                                                          |
    |  MISSOURI          | 12                                                         |
    |  MONTANA           | 2                                                          |
    |  NEBRASKA          | 4                                                          |
    |  NEVADA            | 2                                                          |
    |  NEW HAMPSHIRE     | 2                                                          |
    |  NEW JERSEY        | 8                                                          |
    |  NEW MEXICO        | 4                                                          |
    |  NEW YORK          | 22                                                         |
    |  NORTH CAROLINA    | 12                                                         |
    |  NORTH DAKOTA      | 2                                                          |
    |  OHIO              | 18                                                         |
    |  OKLAHOMA          | 6                                                          |
    |  OREGON            | 7                                                          |
    |  PENNSYLVANIA      | 18                                                         |
    |  RHODE ISLAND      | 2                                                          |
    |  SOUTH CAROLINA    | 7                                                          |
    |  SOUTH DAKOTA      | 2                                                          |
    |  TENNESSEE         | 8                                                          |
    |  TEXAS             | 28                                                         |
    |  UTAH              | 3                                                          |
    |  VERMONT           | 1                                                          |
    |  VIRGINIA          | 16                                                         |
    |  WASHINGTON        | 13                                                         |
    |  WEST VIRGINIA     | 2                                                          |
    |  WISCONSIN         | 8                                                          |
    |  WYOMING           | 1                                                          |
    |  PUERTO RICO       | 3                                                          |
    |                    |                                                            |
    |--------------------+------------------------------------------------------------|

The task is to classify as True all states that have a value greater or equal than 10 in second column::

    $ csvcut -c 1,8 examples/realdata/FY09_EDU_Recipients_by_State.csv | csvpys -s "Classify|bool(int(c[2])>=10) if c[2] != '' else ''" | csvlook
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
    |  DELAWARE          | 1                                                         | False     |
    |  DIST. OF COLUMBIA | 3                                                         | False     |
    |  FLORIDA           | 28                                                        | True      |
    |  GEORGIA           | 13                                                        | True      |
    |  HAWAII            | 3                                                         | False     |
    |  IDAHO             | 2                                                         | False     |
    |  ILLINOIS          | 19                                                        | True      |
    |  INDIANA           | 8                                                         | False     |
    |  IOWA              | 4                                                         | False     |
    |  KANSAS            | 4                                                         | False     |
    |  KENTUCKY          | 6                                                         | False     |
    |  LOUISIANA         | 4                                                         | False     |
    |  MAINE             | 2                                                         | False     |
    |  MARYLAND          | 13                                                        | True      |
    |  MASSACHUSETTS     | 10                                                        | True      |
    |  MICHIGAN          | 16                                                        | True      |
    |  MINNESOTA         | 10                                                        | True      |
    |  MISSISSIPPI       | 3                                                         | False     |
    |  MISSOURI          | 12                                                        | True      |
    |  MONTANA           | 2                                                         | False     |
    |  NEBRASKA          | 4                                                         | False     |
    |  NEVADA            | 2                                                         | False     |
    |  NEW HAMPSHIRE     | 2                                                         | False     |
    |  NEW JERSEY        | 8                                                         | False     |
    |  NEW MEXICO        | 4                                                         | False     |
    |  NEW YORK          | 22                                                        | True      |
    |  NORTH CAROLINA    | 12                                                        | True      |
    |  NORTH DAKOTA      | 2                                                         | False     |
    |  OHIO              | 18                                                        | True      |
    |  OKLAHOMA          | 6                                                         | False     |
    |  OREGON            | 7                                                         | False     |
    |  PENNSYLVANIA      | 18                                                        | True      |
    |  RHODE ISLAND      | 2                                                         | False     |
    |  SOUTH CAROLINA    | 7                                                         | False     |
    |  SOUTH DAKOTA      | 2                                                         | False     |
    |  TENNESSEE         | 8                                                         | False     |
    |  TEXAS             | 28                                                        | True      |
    |  UTAH              | 3                                                         | False     |
    |  VERMONT           | 1                                                         | False     |
    |  VIRGINIA          | 16                                                        | True      |
    |  WASHINGTON        | 13                                                        | True      |
    |  WEST VIRGINIA     | 2                                                         | False     |
    |  WISCONSIN         | 8                                                         | False     |
    |  WYOMING           | 1                                                         | False     |
    |  PUERTO RICO       | 3                                                         | False     |
    |                    |                                                           |           |
    |--------------------+-----------------------------------------------------------+-----------|

.. note::

    If statement is only needed because we need to deal with last line which has empty string ``''``.


OK, within the last example we will calculate number of A's in state names::

    $ csvcut -c 1 examples/realdata/FY09_EDU_Recipients_by_State.csv | csvpys -s "A letter count| collections.Counter(c[1])['A']" | csvlook
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
    |  DELAWARE          | 2               |
    |  DIST. OF COLUMBIA | 1               |
    |  FLORIDA           | 1               |
    |  GEORGIA           | 1               |
    |  HAWAII            | 2               |
    |  IDAHO             | 1               |
    |  ILLINOIS          | 0               |
    |  INDIANA           | 2               |
    |  IOWA              | 1               |
    |  KANSAS            | 2               |
    |  KENTUCKY          | 0               |
    |  LOUISIANA         | 2               |
    |  MAINE             | 1               |
    |  MARYLAND          | 2               |
    |  MASSACHUSETTS     | 2               |
    |  MICHIGAN          | 1               |
    |  MINNESOTA         | 1               |
    |  MISSISSIPPI       | 0               |
    |  MISSOURI          | 0               |
    |  MONTANA           | 2               |
    |  NEBRASKA          | 2               |
    |  NEVADA            | 2               |
    |  NEW HAMPSHIRE     | 1               |
    |  NEW JERSEY        | 0               |
    |  NEW MEXICO        | 0               |
    |  NEW YORK          | 0               |
    |  NORTH CAROLINA    | 2               |
    |  NORTH DAKOTA      | 2               |
    |  OHIO              | 0               |
    |  OKLAHOMA          | 2               |
    |  OREGON            | 0               |
    |  PENNSYLVANIA      | 2               |
    |  RHODE ISLAND      | 1               |
    |  SOUTH CAROLINA    | 2               |
    |  SOUTH DAKOTA      | 2               |
    |  TENNESSEE         | 0               |
    |  TEXAS             | 1               |
    |  UTAH              | 1               |
    |  VERMONT           | 0               |
    |  VIRGINIA          | 1               |
    |  WASHINGTON        | 1               |
    |  WEST VIRGINIA     | 1               |
    |  WISCONSIN         | 0               |
    |  WYOMING           | 0               |
    |  PUERTO RICO       | 0               |
    |                    | 0               |
    |--------------------+-----------------|