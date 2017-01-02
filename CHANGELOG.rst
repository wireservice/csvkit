1.0.2
-----

* :doc:`/scripts/csvjoin` supports ``--snifflimit`` and ``--no-inference``.

1.0.1 - December 29, 2016
-------------------------

This is a minor release which fixes several bugs reported in the :code:`1.0.0` release earlier this week. It also significantly improves the output of :doc:`/scripts/csvstat` and adds a :code:`--csv` output option to that command.

* :doc:`/scripts/csvstat` will no longer crash when a :code:`Number` column has :code:`None` as a frequent value. (#738)
* :doc:`/scripts/csvlook` docs now note that output tables are Markdown-compatible. (#734)
* :doc:`/scripts/csvstat` now supports a :code:`--csv` flag for tabular output. (#584)
* :doc:`/scripts/csvstat` output is now easier to read. (#714)
* :doc:`/scripts/csvpy` now has a better description when using the :code:`--agate` flag (#729)
* Fix a Python 2.6 bug preventing :doc:`/scripts/csvjson` from parsing utf-8 files. (#732)
* Update required version of unittest to latest. (#727)

1.0.0 - December 27, 2016
-------------------------

This is the first major release of csvkit in a very long time. The entire backend has been rewritten to leverage the `agate <http://agate.rtfd.io>`_ data analysis library, which was itself inspired by csvkit. The new backend provides better type detection accuracy, as well as some new features.

Because of the long and complex cycle behind this release, the list of changes should not be considered exhaustive. In particular, the output format of some tools may have changed in small ways. Any existing data pipelines using csvkit should be tested as part of the upgrade.

Much of the credit for this release goes to `James McKinney <https://github.com/jpmckinney>`_, who has almost single-handedly kept the csvkit fire burning for a year. Thanks, James!

Backwards-incompatible changes:

* :doc:`/scripts/csvjoin` now renames duplicate columns with integer suffixes to prevent collisions in output.
* :doc:`/scripts/csvsql` now generates ``DateTime`` columns instead of ``Time`` columns.
* :doc:`/scripts/csvsql` now generates ``Decimal`` columns instead of ``Integer``, ``BigInteger``, and ``Float`` columns.
* :doc:`/scripts/csvsql` no longer generates max-length constraints for text columns.
* The ``--doublequote`` long flag is gone, and the ``-b`` short flag is now an alias for ``--no-doublequote``.
* When using the ``--columns`` or ``--not-columns`` options, you must not have spaces around the comma-separated values, unless the column names contain spaces.
* When sorting, null values are now greater than other values instead of less than.
* ``CSVKitReader``, ``CSVKitWriter``, ``CSVKitDictReader``, and ``CSVKitDictWriter`` have been removed. Use ``agate.csv.reader``, ``agate.csv.writer``, ``agate.csv.DictReader`` and ``agate.csv.DictWriter``.
* Dropped support for older versions of PyPy.
* Dropped Python 2.6 support.
* If ``--no-header-row`` is set, the output will have column names ``a``, ``b``, ``c``, etc. instead of ``column1``, ``column2``, ``column3``, etc.
* csvlook renders a simpler, markdown-compatible table.

Improvements:

* csvkit is now tested against Python 3.6. (#702)
* ``import csvkit as csv`` will now defer to agate readers/writers.
* :doc:`/scripts/csvgrep` supports ``--no-header-row``.
* :doc:`/scripts/csvjoin` supports ``--no-header-row``.
* :doc:`/scripts/csvjson` streams input and output if the ``--stream`` and ``--no-inference`` flags are set.
* :doc:`/scripts/csvjson` supports ``--snifflimit`` and ``--no-inference``.
* :doc:`/scripts/csvlook` adds ``--max-rows``, ``--max-columns`` and ``--max-column-width`` options.
* :doc:`/scripts/csvlook` supports ``--snifflimit`` and ``--no-inference``.
* :doc:`/scripts/csvpy` supports ``--agate`` to read a CSV file into an agate table.
* ``csvsql`` supports custom `SQLAlchemy dialects <http://docs.sqlalchemy.org/en/latest/dialects/>`_.
* :doc:`/scripts/csvstat` supports ``--names``.
* :doc:`/scripts/in2csv` CSV-to-CSV conversion streams input and output if the ``--no-inference`` flag is set.
* :doc:`/scripts/in2csv` CSV-to-CSV conversion uses ``agate.Table``.
* :doc:`/scripts/in2csv` GeoJSON conversion adds columns for geometry type, longitude and latitude.
* Documentation: Update tool usage, remove shell prompts, document connection string, correct typos.

Fixes:

* Fixed numerous instances of open files not being closed before utilities exit.
* Change ``-b``, ``--doublequote`` to ``--no-doublequote``, as doublequote is True by default.
* :doc:`/scripts/in2csv` DBF conversion works with Python 3.
* :doc:`/scripts/in2csv` correctly guesses format when file has an uppercase extension.
* :doc:`/scripts/in2csv` correctly interprets ``--no-inference``.
* :doc:`/scripts/in2csv` again supports nested JSON objects (fixes regression).
* :doc:`/scripts/in2csv` with ``--format geojson`` will print a JSON object instead of ``OrderedDict([(...)])``.
* :doc:`/scripts/csvclean` with standard input works on Windows.
* :doc:`/scripts/csvgrep` returns the input file's line numbers if the ``--linenumbers`` flag is set.
* :doc:`/scripts/csvgrep` can match multiline values.
* :doc:`/scripts/csvgrep` correctly operates on ragged rows.
* :doc:`/scripts/csvsql` correctly escapes ``%``` characters in SQL queries.
* :doc:`/scripts/csvsql` adds standard input only if explicitly requested.
* :doc:`/scripts/csvstack` supports stacking a single file.
* :doc:`/scripts/csvstat` always reports frequencies.
* The ``any_match`` argument of ``FilteringCSVReader`` now works correctly.
* All tools handle empty files without error.

0.9.1 - March 31, 2015
----------------------

* Add Antonio Lima to AUTHORS.
* Add support for ndjson. (#329)
* Add missing docs for csvcut -C. (#227)
* Reorganize docs so TOC works better. (#339)
* Render docs locally with RTD theme.
* Fix header in "tricks" docs.
* Add install instructions to tutorial. (#331)
* Add killer examples to doc index. (#328)
* Reorganize doc index
* Fix broken csvkit module documentation. (#327)
* Fix version of openpyxl to work around encoding issue. (#391, #288)

0.9.0
-----

* Write missing sections of the tutorial. (#32)
* Remove -q arg from sql2csv (conflicts with common flag).
* Fix csvjoin in case where left dataset rows without all columns.
* Rewrote tutorial based on LESO data. (#324)
* Don't error in csvjson if lat/lon columns are null. (#326)
* Maintain field order in output of csvjson.
* Add unit test for json in2csv. (#77)
* Maintain key order when converting JSON into CSV. (#325.)
* Upgrade python-dateutil to version 2.2 (#304)
* Fix sorting of columns with null values. (#302)
* Added release documentation.
* Fill out short rows with null values. (#313)
* Fix unicode output for csvlook and csvstat. (#315)
* Add documentation for --zero. (#323)
* Fix Integrity error when inserting zero rows in database with csvsql. (#299)
* Add Michael Mior to AUTHORS. (#305)
* Add --count option to CSVStat.
* Implement csvformat.
* Fix bug causing CSVKitDictWriter to output 'utf-8' for blank fields.

0.8.0
-----

* Add pnaimoli to AUTHORS.
* Fix column specification in csvstat. (#236)
* Added "Tips and Tricks" documentation. (#297, #298)
* Add Espartaco Palma to AUTHORS.
* Remove unnecessary enumerate calls. (#292)
* Deprecated DBF support for Python 3+.
* Add support for Python 3.3 and 3.4 (#239)

0.7.3
-----

* Fix date handling with openpyxl > 2.0 (#285)
* Add Kristina Durivage to AUTHORS. (#243)
* Added Richard Low to AUTHORS.
* Support SQL queries "directly" on CSV files. (#276)
* Add Tasneem Raja to AUTHORS.
* Fix off-by-one error in open ended column ranges. (#238)
* Add Matt Pettis to AUTHORS.
* Add line numbers flag to csvlook (#244)
* Only install argparse for Python < 2.7. (#224)
* Add Diego Rabatone Oliveira to AUTHORS.
* Add Ryan Murphy to AUTHORS.
* Fix DBF dependency. (#270)

0.7.2
-----

* Fix CHANGELOG for release.

0.7.1
-----

* Fix homepage url in setup.py.

0.7.0
-----

* Fix XLSX datetime normalization bug. (#223)
* Add raistlin7447 to AUTHORS.
* Merged sql2csv utility (#259).
* Add Jeroen Janssens to AUTHORS.
* Validate csvsql DB connections before parsing CSVs. (#257)
* Clarify install process for Ubuntu. (#249)
* Clarify docs for --escapechar. (#242)
* Make ``import csvkit`` API compatible with ``import csv``.
* Update Travis CI link. (#258)
* Add Sébastien Fievet to AUTHORS.
* Use case-sensitive name for SQLAlchemy (#237)
* Add Travis Swicegood to AUTHORS.

0.6.1
-----

* Add Chris Rosenthal to AUTHORS.
* Fix multi-file input to csvsql. (#193)
* Passing --snifflimit=0 to disable dialect sniffing. (#190)
* Add aarcro to the AUTHORS file.
* Improve performance of csvgrep. (#204)
* Add Matt Dudys to AUTHORS.
* Add support for --skipinitialspace. (#201)
* Add Joakim Lundborg to AUTHORS.
* Add --no-inference option to in2csv and csvsql. (#206)
* Add Federico Scrinzi to AUTHORS file.
* Add --no-header-row to all tools. (#189)
* Fix csvstack blowing up on empty files. (#209)
* Add Chris Rosenthal to AUTHORS file.
* Add --db-schema option to csvsql. (#216)
* Add Shane StClair to AUTHORS file.
* Add --no-inference support to csvsort. (#222)

0.5.0
-----

* Implement geojson support in csvjson. (#159)
* Optimize writing of eight bit codecs. (#175)
* Created csvpy. (#44)
* Support --not-columns for excluding columns. (#137)
* Add Jan Schulz to AUTHORS file.
* Add Windows scripts. (#111, #176)
* csvjoin, csvsql and csvstack will no longer hold open all files. (#178)
* Added Noah Hoffman to AUTHORS.
* Make csvlook output compatible with emacs table markup. (#174)

0.4.4
-----

* Add Derek Wilson to AUTHORS.
* Add Kevin Schaul to AUTHORS.
* Add DBF support to in2csv. (#11, #160)
* Support --zero option for zero-based column indexing. (#144)
* Support mixing nulls and blanks in string columns.
* Add --blanks option to csvsql. (#149)
* Add multi-file (glob) support to csvsql. (#146)
* Add Gregory Temchenko to AUTHORS.
* Add --no-create option to csvsql. (#148)
* Add Anton Ian Sipos to AUTHORS.
* Fix broken pipe errors. (#150)

0.4.3
-----

* Begin CHANGELOG (a bit late, I'll admit).
