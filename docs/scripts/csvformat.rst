=========
csvformat
=========

Description
===========

Convert a CSV file to a custom output format.:

.. code-block:: none

   usage: csvformat [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                    [-p ESCAPECHAR] [-z FIELD_SIZE_LIMIT] [-e ENCODING]
                    [-L LOCALE] [-S] [-H] [-K SKIP_LINES] [-v] [-l] [--zero] [-V]
                    [--describe] [-y SNIFF_LIMIT] [-E] [-D OUT_DELIMITER] [-T] [-A] [-Q OUT_QUOTECHAR]
                    [-U {0,1,2,3}] [-B] [-P OUT_ESCAPECHAR]
                    [-M OUT_LINETERMINATOR]
                    [FILE]

   Convert a CSV file to a custom output format.

   positional arguments:
     FILE                  The CSV file to operate on. If omitted, will accept
                           input as piped data via STDIN.

   optional arguments:
     -h, --help            show this help message and exit
     --describe            Describe the input CSV dialect instead of converting
                           the file.
     -y SNIFF_LIMIT, --snifflimit SNIFF_LIMIT
                           For --describe, limit dialect sniffing to this many
                           characters (default: 1024). Use 0 to disable sniffing
                           or -1 to sniff the entire file.
     -E, --skip-header     Do not output a header row.
     -D OUT_DELIMITER, --out-delimiter OUT_DELIMITER
                           Delimiting character of the output file.
     -T, --out-tabs        Specify that the output file is delimited with tabs.
                           Overrides "-D".
     -A, --out-asv         Specify that the output file is delimited with the
                           ASCII unit separator and record separator. Overrides
                           "-T", "-D" and "-M".
     -Q OUT_QUOTECHAR, --out-quotechar OUT_QUOTECHAR
                           Character used to quote strings in the output file.
     -U {0,1,2,3}, --out-quoting {0,1,2,3}
                           Quoting style used in the output file: 0 quote
                           minimal, 1 quote all, 2 quote non-numeric, 3 quote
                           none.
     -B, --out-no-doublequote
                           Whether or not double quotes are doubled in the output
                           file.
     -P OUT_ESCAPECHAR, --out-escapechar OUT_ESCAPECHAR
                           Character used to escape the delimiter in the output
                           file if --quoting 3 ("Quote None") is specified and to
                           escape the QUOTECHAR if --out-no-doublequote is
                           specified.
     -M OUT_LINETERMINATOR, --out-lineterminator OUT_LINETERMINATOR
                           Character used to terminate lines in the output file.

See also: :doc:`../common_arguments`.

Examples
========

Inspect the input dialect, including the detected delimiter:

.. code-block:: bash

   csvformat --describe data.csv
   csvformat --describe -y -1 data.csv

:code:`--describe` uses agate's dialect sniffer and applies explicit input options
such as :code:`-d`, :code:`-t` and :code:`-q` after sniffing. It reports the effective
reader settings and does not parse data rows or convert the input. Output-format
options do not affect the report. Sniffing can fail or guess incorrectly; if it
fails, agate warns and the reader uses its defaults and any explicit input options.
Line terminators are not reported because the sniffer does not detect them.
:code:`-y` only affects :code:`--describe`; normal conversion does not sniff.

Convert a comma-separated file to a pipe-delimited file:

.. code-block:: bash

   csvformat -D "|" examples/dummy.csv

Convert to carriage return line-endings:

.. code-block:: bash

   csvformat -M $'\r' examples/dummy.csv

Convert to a tab-delimited file (TSV) with no doubling of double quotes:

.. code-block:: bash

   printf 'key,value\n1,"a ""quoted"" string"' | csvformat -T -Q🐍

To avoid escaping quote characters when using :code:`--quoting 3`, add :code:`--out-quotechar ""`:

.. code-block:: bash

   csvformat -u3 -U3 -Q🐍 examples/optional_quote_characters.csv
