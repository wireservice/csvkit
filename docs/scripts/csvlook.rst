=======
csvlook
=======

Description
===========

Renders a CSV to the command line in a readable, fixed-width format::

    usage: csvlook [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                   [-p ESCAPECHAR] [-z MAXFIELDSIZE] [-e ENCODING] [-S] [-H] [-v]
                   [-l] [--zero]
                   [FILE]

    Render a CSV file in the console as a fixed-width table.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      --max-rows MAX_ROWS   The maximum number of rows to display before
                            truncating the data.
      --max-columns MAX_COLUMNS
                            The maximum number of columns to display before
                            truncating the data.
      --max-column-width MAX_COLUMN_WIDTH
                            Truncate all columns to at most this width. The
                            remainder will be replaced with ellipsis.
      -y SNIFF_LIMIT, --snifflimit SNIFF_LIMIT
                            Limit CSV dialect sniffing to the specified number of
                            bytes. Specify "0" to disable sniffing entirely.
      --no-inference        Disable type inference when parsing the input.

If a table is too wide to display properly try piping the output to ``less -S`` or truncating it using :doc:`csvcut`.

If the table is too long, try filtering it down with grep or piping the output to ``less``.

See also: :doc:`../common_arguments`.

Examples
========

Basic use::

    csvlook examples/testfixed_converted.csv

This tool is especially useful as a final operation when piping through other tools::

    csvcut -c 9,1 examples/realdata/FY09_EDU_Recipients_by_State.csv | csvlook
