========
csvclean
========

Description
===========

Cleans a CSV file of common syntax errors. Outputs [basename]_out.csv and [basename]_err.csv, the former containing all valid rows and the latter containing all error rows along with line numbers and descriptions.

Examples
========

Test a file with known bad rows::

    csvclean examples/bad.csv
