Unreleased
----------

-  feat: Add a :code:`--no-leading-zeroes` option to tools that support type inference.
-  feat: :doc:`/scripts/csvsql` adds a :code:`--engine-option` option.
-  feat: :doc:`/scripts/csvsql` adds a :code:`--sql-delimiter` option, to set a different delimiter than ``;`` for the :code:`--query`, :code:`--before-insert` and :code:`after-insert` options.
-  feat: :doc:`/scripts/sql2csv` adds a :code:`--execution-option` option.
-  feat: :doc:`/scripts/sql2csv` uses the ``stream_results=True`` execution option, by default, to not load all data into memory at once.
-  fix: :doc:`/scripts/csvsql` uses a default value of 1 for the :code:`--min-col-len` and :code:`--col-len-multiplier` options.

2.0.1 - July 12, 2024
---------------------

-  feat: :doc:`/scripts/csvsql` adds :code:`--min-col-len` and :code:`--col-len-multiplier` options.
-  feat: :doc:`/scripts/sql2csv` adds a :code:`--engine-option` option.
-  feat: Add a Docker image: ``docker pull ghcr.io/wireservice/csvkit:latest``.
-  feat: Add man pages to the sdist and wheel distributions.
-  fix: :doc:`/scripts/csvstat` no longer errors when a column is a time delta and :code:`--json` is set.
-  fix: When taking arguments from ``sys.argv`` on Windows, glob patterns, user directories, and environment variables are expanded.

2.0.0 - May 1, 2024
-------------------

This is the first major release since December 27, 2016. Thank you to all :ref:`contributors<authors>`, including 44 new contributors since 1.0.0!

Want to use csvkit programmatically? Check out `agate <https://agate.readthedocs.io/en/latest/>`__, used internally by csvkit.

**BACKWARDS-INCOMPATIBLE CHANGES:**

-  :doc:`/scripts/csvclean` now writes its output to standard output and its errors to standard error, instead of to ``basename_out.csv`` and ``basename_err.csv`` files. Consequently:

   -  The :code:`--dry-run` option is removed. The :code:`--dry-run` option changed error output from the CSV format used in ``basename_err.csv`` files to a prosaic format like ``Line 1: Expected 2 columns, found 3 columns``.
   -  Summary information like ``No errors.``, ``42 errors logged to basename_err.csv`` and ``42 rows were joined/reduced to 24 rows after eliminating expected internal line breaks.`` is not written.

-  :doc:`/scripts/csvclean` no longer reports or fixes errors by default; it errors if no checks or fixes are enabled. Opt in to the original behavior using the :code:`--length-mismatch` and :code:`--join-short-rows` options. See new options below.
-  :doc:`/scripts/csvclean` no longer omits rows with errors from the output. Opt in to the original behavior using the :code:`--omit-error-rows` option.
-  :doc:`/scripts/csvclean` joins short rows using a newline by default, instead of a space. Restore the original behavior using the :code:`--separator " "` option.

In brief, to restore the original behavior for :doc:`/scripts/csvclean`:

.. code-block:: bash

   csvclean --length-mismatch --omit-error-rows --join-short-rows --separator " " myfile.csv

Other changes:

-  feat: :doc:`/scripts/csvclean` adds the options:

   -  :code:`--length-mismatch`, to error on data rows that are shorter or longer than the header row
   -  :code:`--empty-columns`, to error on empty columns
   -  :code:`--enable-all-checks`, to enable all error reporting
   -  :code:`--omit-error-rows`, to omit data rows that contain errors, from standard output
   -  :code:`--label LABEL`, to add a "label" column to standard error
   -  :code:`--header-normalize-space`, to strip leading and trailing whitespace and replace sequences of whitespace characters by a single space in the header
   -  :code:`--join-short-rows`, to merge short rows into a single row
   -  :code:`--separator SEPARATOR`, to change the string with which to join short rows (default is newline)
   -  :code:`--fill-short-rows`, to fill short rows with the missing cells
   -  :code:`--fillvalue FILLVALUE`, to change the value with which to fill short rows (default is none)

-  feat: The :code:`--quoting` option accepts 4 (`csv.QUOTE_STRINGS <https://docs.python.org/3/library/csv.html#csv.QUOTE_STRINGS>`__) and 5 (`csv.QUOTE_NOTNULL <https://docs.python.org/3/library/csv.html#csv.QUOTE_NOTNULL>`__) on Python 3.12.
-  feat: :doc:`/scripts/csvformat`: The :code:`--out-quoting` option accepts 4 (`csv.QUOTE_STRINGS <https://docs.python.org/3/library/csv.html#csv.QUOTE_STRINGS>`__) and 5 (`csv.QUOTE_NOTNULL <https://docs.python.org/3/library/csv.html#csv.QUOTE_NOTNULL>`__) on Python 3.12.
-  fix: :doc:`/scripts/csvformat`: The :code:`--out-quoting` option works with 2 (`csv.QUOTE_NONUMERIC <https://docs.python.org/3/library/csv.html#csv.QUOTE_NOTNUMERIC>`__). Use the :code:`--locale` option to set the locale of any formatted numbers.
-  fix: :doc:`/scripts/csvclean`: The :code:`--join-short-rows` option no longer reports length mismatch errors that were fixed.

1.5.0 - March 28, 2024
----------------------

-  feat: Add support for Zstandard files with the ``.zst`` extension, if the ``zstandard`` package is installed.
-  feat: :doc:`/scripts/csvformat` adds a :code:`--out-asv` (:code:`--A`) option to use the ASCII unit separator and record separator.
-  feat: :doc:`/scripts/csvsort` adds a :code:`--ignore-case` (:code:`--i`) option to perform case-independent sorting.

1.4.0 - February 13, 2024
-------------------------

-  feat: :doc:`/scripts/csvpy` adds the options:

   -  :code:`--no-number-ellipsis`, to disable the ellipsis (``…``) if max precision is exceeded, for example, when using ``table.print_table()``
   -  :code:`--sniff-limit``
   -  :code:`--no-inference``

-  feat: :doc:`/scripts/csvpy` removes the :code:`--linenumbers` and :code:`--zero` output options, which had no effect.
-  feat: :doc:`/scripts/in2csv` adds a :code:`--reset-dimensions` option to `recalculate <https://openpyxl.readthedocs.io/en/stable/optimized.html#worksheet-dimensions>`_ the dimensions of an XLSX file, instead of trusting the file's metadata. csvkit's dependency `agate-excel <https://agate-excel.readthedocs.io/en/latest/>`_ 0.4.0 automatically recalculates the dimensions if the file's metadata expresses dimensions of "A1:A1" (a single cell).
-  fix: :doc:`/scripts/csvlook` only reads up to :code:`--max-rows` rows instead of the entire file.
-  fix: :doc:`/scripts/csvpy` supports the existing input options:

   -  :code:`--locale`
   -  :code:`--blanks`
   -  :code:`--null-value`
   -  :code:`--date-format`
   -  :code:`--datetime-format`
   -  :code:`--skip-lines`

-  fix: :doc:`/scripts/csvpy`: :code:`--maxfieldsize` no longer errors when :code:`--dict` is set.
-  fix: :doc:`/scripts/csvstack`: :code:`--maxfieldsize` no longer errors when :code:`--no-header-row` isn't set.
-  fix: :doc:`/scripts/in2csv`: :code:`--write-sheets` no longer errors when standard input is an XLS or XLSX file.
-  Update minimum agate version to 1.6.3.

1.3.0 - October 18, 2023
------------------------

-  :doc:`/scripts/csvformat` adds a :code:`--skip-header` (:code:`-E`) option to not output a header row.
-  :doc:`/scripts/csvlook` adds a :code:`--max-precision` option to set the maximum number of decimal places to display.
-  :doc:`/scripts/csvlook` adds a :code:`--no-number-ellipsis` option to disable the ellipsis (``…``) if :code:`--max-precision` is exceeded. (Requires agate 1.9.0 or greater.)
-  :doc:`/scripts/csvstat` supports the :code:`--no-inference` (:code:`-I`), :code:`--locale` (:code:`-L`), :code:`--blanks`, :code:`--date-format` and :code:`datetime-format` options.
-  :doc:`/scripts/csvstat` reports a "Non-null values" statistic (or a :code:`nonnulls` column when :code:`--csv` is set).
-  :doc:`/scripts/csvstat` adds a :code:`--non-nulls` option to only output counts of non-null values.
-  :doc:`/scripts/csvstat` reports a "Most decimal places" statistic (or a :code:`maxprecision` column when :code:`--csv` is set).
-  :doc:`/scripts/csvstat` adds a :code:`--max-precision` option to only output the most decimal places.
-  :doc:`/scripts/csvstat` adds a :code:`--json` option to output results as JSON text.
-  :doc:`/scripts/csvstat` adds an :code:`--indent` option to indent the JSON text when :code:`--json` is set.
-  :doc:`/scripts/in2csv` adds a :code:`--use-sheet-names` option to use the sheet names as file names when :code:`--write-sheets` is set.
-  feat: Add a :code:`--null-value` option to commands with the :code:`--blanks` option, to convert additional values to NULL.
-  fix: Reconfigure the encoding of standard input according to the :code:`--encoding` option, which defaults to ``utf-8-sig``. Affected users no longer need to set the ``PYTHONIOENCODING`` environment variable.
-  fix: Prompt the user if additional input is expected (i.e. if no input file or piped data is provided) in :doc:`/scripts/csvjoin`, :doc:`/scripts/csvsql` and :doc:`/scripts/csvstack`.
-  fix: No longer errors if a NUL byte occurs in an input file.
-  Add Python 3.12 support.

1.2.0 - October 4, 2023
-----------------------

-  fix: :doc:`/scripts/csvjoin` uses the correct columns when performing a :code:`--right` join.
-  Add SQLAlchemy 2 support.
-  Drop Python 3.7 support (end-of-life was June 5, 2023).

1.1.1 - February 22, 2023
-------------------------

-  feat: :doc:`/scripts/csvstack` handles files with columns in different orders or with different names.

1.1.0 - January 3, 2023
-----------------------

-  feat: :doc:`/scripts/csvsql` accepts multiple :code:`--query` command-line arguments.
-  feat: :doc:`/scripts/csvstat` adds :code:`--no-grouping-separator` and :code:`--decimal-format` options.
-  Add Python 3.11 support.
-  Drop Python 3.6 support (end-of-life was December 23, 2021).
-  Drop Python 2.7 support (end-of-life was January 1, 2020).

1.0.7 - March 6, 2022
---------------------

-  fix: :doc:`/scripts/csvcut` extracts the correct columns when :code:`--line-numbers` is set.
-  fix: Restore Python 2.7 support in edge cases.
-  feat: Use 1024 byte sniff-limit by default across csvkit. Improve csvstat performance up to 10x.
-  feat: Add support for ``.xz`` (LZMA) compressed input files.
-  Add Python 3.10 support.
-  Drop Python 3.5 support (end-of-life was September 30, 2020).

1.0.6 - July 13, 2021
---------------------

Changes:

-  :doc:`/scripts/csvstat` no longer prints "Row count: " when :code:`--count` is set.
-  :doc:`/scripts/csvclean`, :doc:`/scripts/csvcut`, :doc:`/scripts/csvgrep` no longer error if standard input is null.

Fixes:

-  :doc:`/scripts/csvformat` creates default headers when :code:`--no-header-row` is set, as documented.
-  :doc:`/scripts/csvstack` no longer errors when :code:`--no-header-row` is combined with :code:`--groups` or :code:`--filenames`.

1.0.5 - March 2, 2020
---------------------

Changes:

-  Drop Python 3.4 support (end-of-life was March 18, 2019).

Improvements:

-  Output error message for memory error even if not :code:`--verbose`.

Fixes:

-  Fix regression in 1.0.4, which caused numbers like ``4.5`` to be parsed as dates.
-  :doc:`/scripts/in2csv` Fix error reporting if :code:`--names` used with non-Excel file.

1.0.4 - March 16, 2019
----------------------

Changes:

-  Drop Python 3.3 support (end-of-life was September 29, 2017).

Improvements:

-  :doc:`/scripts/csvsql` adds a :code:`--chunk-size` option to set the chunk size when batch inserting into a table.
-  csvkit is tested against Python 3.7.

Fixes:

-  :code:`--names` works with :code:`--skip-lines`.
-  Dates and datetimes without punctuation can be parsed with :code:`--date-format` and :code:`datetime-format`.
-  Error messages about column indices use 1-based numbering unless :code:`--zero` is set.
-  :doc:`/scripts/csvcut` no longer errors on :code:`--delete-empty-rows` with short rows.
-  :doc:`/scripts/csvjoin` no longer errors if given a single file.
-  :doc:`/scripts/csvsql` supports UPDATE commands.
-  :doc:`/scripts/csvstat` no longer errors on non-finite numbers.
-  :doc:`/scripts/csvstat` respects all command-line arguments when :code:`--count` is set.
-  :doc:`/scripts/in2csv` CSV-to-CSV conversion respects :code:`--linenumbers` when buffering.
-  :doc:`/scripts/in2csv` writes XLS sheets without encoding errors in Python 2.

1.0.3 - March 11, 2018
----------------------

Improvements:

-  :doc:`/scripts/csvgrep` adds a :code:`--any-match` (:code:`-a`) flag to select rows where any column matches instead of all columns.
-  :doc:`/scripts/csvjson` no longer emits a property if its value is null.
-  :doc:`/scripts/csvjson` adds :code:`--type` and :code:`--geometry` options to emit non-Point GeoJSON features.
-  :doc:`/scripts/csvjson` adds a :code:`--no-bbox` option to disable the calculation of a bounding box.
-  :doc:`/scripts/csvjson` supports :code:`--stream` for newline-delimited GeoJSON.
-  :doc:`/scripts/csvsql` adds a :code:`--unique-constraint` option to list names of columns to include in a UNIQUE constraint.
-  :doc:`/scripts/csvsql` adds :code:`--before-insert` and :code:`--after-insert` options to run commands before and after the INSERT command.
-  :doc:`/scripts/csvpy` reports an error message if input is provided via STDIN.
-  :doc:`/scripts/in2csv` adds a :code:`--encoding-xls` option to specify the encoding of the input XLS file.
-  :doc:`/scripts/in2csv` supports :code:`--no-header-row` on XLS and XLSX files.
-  Suppress agate warning about column names not specified when using :code:`--no-header-row`.
-  Prompt the user if additional input is expected (i.e. if no input file or piped data is provided).
-  Update to `agate-excel 0.2.2 <https://agate-excel.readthedocs.io/en/latest/#changelog>`_, `agate-sql 0.5.3 <https://agate-sql.readthedocs.io/en/latest/#changelog>`_.

Fixes:

-  :doc:`/scripts/csvgrep` accepts utf-8 arguments to the :code:`--match` and :code:`--regex` options in Python 2.
-  :doc:`/scripts/csvjson` streams input and output only if :code:`--snifflimit` is :code:`0`.
-  :doc:`/scripts/csvsql` sets a DECIMAL's precision and scale and a VARCHAR's length to avoid dialect-specific errors.
-  :doc:`/scripts/csvstack` no longer opens all files at once.
-  :doc:`/scripts/in2csv` respects :code:`--no-header-row` when :code:`--no-inference` is set.
-  :doc:`/scripts/in2csv` CSV-to-CSV conversion streams input and output only if :code:`--snifflimit` is :code:`0`.
-  :doc:`/scripts/in2csv` supports GeoJSON files with: ``geometry`` set to ``null``, missing Point ``coordinates``, altitude coordinate values.

csvkit is no longer tested on PyPy.

1.0.2 - April 28, 2017
----------------------

Improvements:

-  Add a :code:`--version` flag.
-  Add a :code:`--skip-lines` option to skip initial lines (e.g. comments, copyright notices, empty rows).
-  Add a :code:`--locale` option to set the locale of any formatted numbers.
-  Add a :code:`--date-format` option to set a strptime date format string.
-  Add a :code:`--datetime-format` option to set a strptime datetime format string.
-  Make :code:`--blanks` a common argument across all tools.
-  :code:`-I` is the short option for :code:`--no-inference`.
-  :doc:`/scripts/csvclean`, :doc:`/scripts/csvformat`, :doc:`/scripts/csvjson`, :doc:`/scripts/csvpy` support :code:`--no-header-row`.
-  :doc:`/scripts/csvclean` is faster and no longer requires exponential time in the worst case.
-  :doc:`/scripts/csvformat` supports :code:`--linenumbers` and `--zero` (no-op).
-  :doc:`/scripts/csvjoin` supports :code:`--snifflimit` and :code:`--no-inference`.
-  :doc:`/scripts/csvpy` supports :code:`--linenumbers` (no-op) and :code:`--zero` (no-op).
-  :doc:`/scripts/csvsql` adds a :code:`--prefix` option to add expressions like OR IGNORE or OR REPLACE following the INSERT keyword.
-  :doc:`/scripts/csvsql` adds a :code:`--overwrite` flag to drop any existing table with the same name before creating.
-  :doc:`/scripts/csvsql` accepts a file name for the :code:`--query` option.
-  :doc:`/scripts/csvsql` supports :code:`--linenumbers` (no-op).
-  :doc:`/scripts/csvsql` adds a :code:`--create-if-not-exists` flag to not abort if the table already exists.
-  :doc:`/scripts/csvstat` adds a :code:`--freq-count` option to set the maximum number of frequent values to display.
-  :doc:`/scripts/csvstat` supports :code:`--linenumbers` (no-op).
-  :doc:`/scripts/in2csv` adds a :code:`--names` flag to print Excel sheet names.
-  :doc:`/scripts/in2csv` adds a :code:`--write-sheets` option to write the named Excel sheets to files.
-  :doc:`/scripts/sql2csv` adds an :code:`--encoding` option to specify the encoding of the input query file.

Fixes:

-  :doc:`/scripts/csvgrep` no longer ignores common arguments if :code:`--linenumbers` is set.
-  :doc:`/scripts/csvjson` supports Decimal.
-  :doc:`/scripts/csvpy` again supports IPython.
-  :doc:`/scripts/csvsql` restores support for :code:`--no-constraints` and :code:`--db-schema`.
-  :doc:`/scripts/csvstat` no longer crashes when :code:`--freq` is set.
-  :doc:`/scripts/in2csv` restores support for :code:`--no-inference` for Excel files.
-  :doc:`/scripts/in2csv` restores support for converting Excel files from standard input.
-  :doc:`/scripts/in2csv` accepts utf-8 arguments to the :code:`--sheet` option in Python 2.

1.0.1 - December 29, 2016
-------------------------

This is a minor release which fixes several bugs reported in the :code:`1.0.0` release earlier this week. It also significantly improves the output of :doc:`/scripts/csvstat` and adds a :code:`--csv` output option to that command.

-  :doc:`/scripts/csvstat` no longer crashes when a :code:`Number` column has :code:`None` as a frequent value. (#738)
-  :doc:`/scripts/csvlook` documents that output tables are Markdown-compatible. (#734)
-  :doc:`/scripts/csvstat` adds a :code:`--csv` flag for tabular output. (#584)
-  :doc:`/scripts/csvstat` output is easier to read. (#714)
-  :doc:`/scripts/csvpy` has a better description when using the :code:`--agate` flag. (#729)
-  Fix a Python 2.6 bug preventing :doc:`/scripts/csvjson` from parsing utf-8 files. (#732)
-  Update required version of unittest to latest. (#727)

1.0.0 - December 27, 2016
-------------------------

This is the first major release of csvkit in a very long time. The entire backend has been rewritten to leverage the `agate <https://agate.rtfd.io>`_ data analysis library, which was itself inspired by csvkit. The new backend provides better type detection accuracy, as well as some new features.

Because of the long and complex cycle behind this release, the list of changes should not be considered exhaustive. In particular, the output format of some tools may have changed in small ways. Any existing data pipelines using csvkit should be tested as part of the upgrade.

Much of the credit for this release goes to `James McKinney <https://github.com/jpmckinney>`_, who has almost single-handedly kept the csvkit fire burning for a year. Thanks, James!

Backwards-incompatible changes:

-  :doc:`/scripts/csvjoin` renames duplicate columns with integer suffixes to prevent collisions in output.
-  :doc:`/scripts/csvsql` generates ``DateTime`` columns instead of ``Time`` columns.
-  :doc:`/scripts/csvsql` generates ``Decimal`` columns instead of ``Integer``, ``BigInteger``, and ``Float`` columns.
-  :doc:`/scripts/csvsql` no longer generates max-length constraints for text columns.
-  The ``--doublequote`` long flag is gone, and the ``-b`` short flag is an alias for ``--no-doublequote``.
-  When using the ``--columns`` or ``--not-columns`` options, you must not have spaces around the comma-separated values, unless the column names contain spaces.
-  When sorting, null values are greater than other values instead of less than.
-  ``CSVKitReader``, ``CSVKitWriter``, ``CSVKitDictReader``, and ``CSVKitDictWriter`` have been removed. Use ``agate.csv.reader``, ``agate.csv.writer``, ``agate.csv.DictReader`` and ``agate.csv.DictWriter``.
-  Drop Python 2.6 support (end-of-life was October 29, 2013).
-  Drop support for older versions of PyPy.
-  If ``--no-header-row`` is set, the output has column names ``a``, ``b``, ``c``, etc. instead of ``column1``, ``column2``, ``column3``, etc.
-  csvlook renders a simpler, markdown-compatible table.

Improvements:

-  csvkit is tested against Python 3.6. (#702)
-  ``import csvkit as csv`` defers to agate readers/writers.
-  :doc:`/scripts/csvgrep` supports ``--no-header-row``.
-  :doc:`/scripts/csvjoin` supports ``--no-header-row``.
-  :doc:`/scripts/csvjson` streams input and output if the ``--stream`` and ``--no-inference`` flags are set.
-  :doc:`/scripts/csvjson` supports ``--snifflimit`` and ``--no-inference``.
-  :doc:`/scripts/csvlook` adds ``--max-rows``, ``--max-columns`` and ``--max-column-width`` options.
-  :doc:`/scripts/csvlook` supports ``--snifflimit`` and ``--no-inference``.
-  :doc:`/scripts/csvpy` supports ``--agate`` to read a CSV file into an agate table.
-  ``csvsql`` supports custom `SQLAlchemy dialects <https://docs.sqlalchemy.org/en/latest/dialects/>`_.
-  :doc:`/scripts/csvstat` supports ``--names``.
-  :doc:`/scripts/in2csv` CSV-to-CSV conversion streams input and output if the ``--no-inference`` flag is set.
-  :doc:`/scripts/in2csv` CSV-to-CSV conversion uses ``agate.Table``.
-  :doc:`/scripts/in2csv` GeoJSON conversion adds columns for geometry type, longitude and latitude.
-  Documentation: Update tool usage, remove shell prompts, document connection string, correct typos.

Fixes:

-  Fixed numerous instances of open files not being closed before utilities exit.
-  Change ``-b``, ``--doublequote`` to ``--no-doublequote``, as doublequote is True by default.
-  :doc:`/scripts/in2csv` DBF conversion works with Python 3.
-  :doc:`/scripts/in2csv` correctly guesses format when file has an uppercase extension.
-  :doc:`/scripts/in2csv` correctly interprets ``--no-inference``.
-  :doc:`/scripts/in2csv` again supports nested JSON objects (fixes regression).
-  :doc:`/scripts/in2csv` with ``--format geojson`` prints a JSON object instead of ``OrderedDict([(...)])``.
-  :doc:`/scripts/csvclean` with standard input works on Windows.
-  :doc:`/scripts/csvgrep` returns the input file's line numbers if the ``--linenumbers`` flag is set.
-  :doc:`/scripts/csvgrep` can match multiline values.
-  :doc:`/scripts/csvgrep` correctly operates on ragged rows.
-  :doc:`/scripts/csvsql` correctly escapes ``%``` characters in SQL queries.
-  :doc:`/scripts/csvsql` adds standard input only if explicitly requested.
-  :doc:`/scripts/csvstack` supports stacking a single file.
-  :doc:`/scripts/csvstat` always reports frequencies.
-  The ``any_match`` argument of ``FilteringCSVReader`` works correctly.
-  All tools handle empty files without error.

0.9.1 - March 31, 2015
----------------------

-  Add Antonio Lima to AUTHORS.
-  Add support for ndjson. (#329)
-  Add missing docs for csvcut -C. (#227)
-  Reorganize docs so TOC works better. (#339)
-  Render docs locally with RTD theme.
-  Fix header in "tricks" docs.
-  Add install instructions to tutorial. (#331)
-  Add killer examples to doc index. (#328)
-  Reorganize doc index
-  Fix broken csvkit module documentation. (#327)
-  Fix version of openpyxl to work around encoding issue. (#391, #288)

0.9.0 - September 8, 2014
-------------------------

-  Write missing sections of the tutorial. (#32)
-  Remove -q arg from sql2csv (conflicts with common flag).
-  Fix csvjoin in case where left dataset rows without all columns.
-  Rewrote tutorial based on LESO data. (#324)
-  Don't error in csvjson if lat/lon columns are null. (#326)
-  Maintain field order in output of csvjson.
-  Add unit test for json in2csv. (#77)
-  Maintain key order when converting JSON into CSV. (#325.)
-  Upgrade python-dateutil to version 2.2 (#304)
-  Fix sorting of columns with null values. (#302)
-  Added release documentation.
-  Fill out short rows with null values. (#313)
-  Fix unicode output for csvlook and csvstat. (#315)
-  Add documentation for --zero. (#323)
-  Fix Integrity error when inserting zero rows in database with csvsql. (#299)
-  Add Michael Mior to AUTHORS. (#305)
-  Add --count option to CSVStat.
-  Implement csvformat.
-  Fix bug causing CSVKitDictWriter to output 'utf-8' for blank fields.

0.8.0 - July 27, 2014
---------------------

-  Add pnaimoli to AUTHORS.
-  Fix column specification in csvstat. (#236)
-  Added "Tips and Tricks" documentation. (#297, #298)
-  Add Espartaco Palma to AUTHORS.
-  Remove unnecessary enumerate calls. (#292)
-  Deprecated DBF support for Python 3+.
-  Add support for Python 3.3 and 3.4 (#239)

0.7.3 - April 27, 2014
----------------------

-  Fix date handling with openpyxl > 2.0 (#285)
-  Add Kristina Durivage to AUTHORS. (#243)
-  Added Richard Low to AUTHORS.
-  Support SQL queries "directly" on CSV files. (#276)
-  Add Tasneem Raja to AUTHORS.
-  Fix off-by-one error in open ended column ranges. (#238)
-  Add Matt Pettis to AUTHORS.
-  Add line numbers flag to csvlook (#244)
-  Only install argparse for Python < 2.7. (#224)
-  Add Diego Rabatone Oliveira to AUTHORS.
-  Add Ryan Murphy to AUTHORS.
-  Fix DBF dependency. (#270)

0.7.2 - March 24, 2014
----------------------

-  Fix CHANGELOG for release.

0.7.1 - March 24, 2014
----------------------

-  Fix homepage url in setup.py.

0.7.0 - March 24, 2014
----------------------

-  Fix XLSX datetime normalization bug. (#223)
-  Add raistlin7447 to AUTHORS.
-  Merged sql2csv utility (#259).
-  Add Jeroen Janssens to AUTHORS.
-  Validate csvsql DB connections before parsing CSVs. (#257)
-  Clarify install process for Ubuntu. (#249)
-  Clarify docs for --escapechar. (#242)
-  Make ``import csvkit`` API compatible with ``import csv``.
-  Update Travis CI link. (#258)
-  Add Sébastien Fievet to AUTHORS.
-  Use case-sensitive name for SQLAlchemy (#237)
-  Add Travis Swicegood to AUTHORS.

0.6.1 - August 20, 2013
-----------------------

-  Fix CHANGELOG for release.

0.6.0 - August 20, 2013
-----------------------

-  Add Chris Rosenthal to AUTHORS.
-  Fix multi-file input to csvsql. (#193)
-  Passing --snifflimit=0 to disable dialect sniffing. (#190)
-  Add aarcro to the AUTHORS file.
-  Improve performance of csvgrep. (#204)
-  Add Matt Dudys to AUTHORS.
-  Add support for --skipinitialspace. (#201)
-  Add Joakim Lundborg to AUTHORS.
-  Add --no-inference option to in2csv and csvsql. (#206)
-  Add Federico Scrinzi to AUTHORS file.
-  Add --no-header-row to all tools. (#189)
-  Fix csvstack blowing up on empty files. (#209)
-  Add Chris Rosenthal to AUTHORS file.
-  Add --db-schema option to csvsql. (#216)
-  Add Shane StClair to AUTHORS file.
-  Add --no-inference support to csvsort. (#222)

0.5.0 - August 21, 2012
-----------------------

-  Implement geojson support in csvjson. (#159)
-  Optimize writing of eight bit codecs. (#175)
-  Created csvpy. (#44)
-  Support --not-columns for excluding columns. (#137)
-  Add Jan Schulz to AUTHORS file.
-  Add Windows scripts. (#111, #176)
-  csvjoin, csvsql and csvstack no longer hold open all files. (#178)
-  Added Noah Hoffman to AUTHORS.
-  Make csvlook output compatible with emacs table markup. (#174)

0.4.4 - May 1, 2012
-------------------

-  Add Derek Wilson to AUTHORS.
-  Add Kevin Schaul to AUTHORS.
-  Add DBF support to in2csv. (#11, #160)
-  Support --zero option for zero-based column indexing. (#144)
-  Support mixing nulls and blanks in string columns.
-  Add --blanks option to csvsql. (#149)
-  Add multi-file (glob) support to csvsql. (#146)
-  Add Gregory Temchenko to AUTHORS.
-  Add --no-create option to csvsql. (#148)
-  Add Anton Ian Sipos to AUTHORS.
-  Fix broken pipe errors. (#150)

0.4.3 - February 20, 2012
-------------------------

-  Begin CHANGELOG (a bit late, I'll admit).
