=======
csvsed
=======

Description
===========

A stream-oriented CSV modification tool. Like a stripped-down "sed" command,
but for tabular data::

    usage: cli.py [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                  [-p ESCAPECHAR] [-z FIELD_SIZE_LIMIT] [-e ENCODING] [-S] [-H]
                  [-v] [-l] [--zero] [-n] [-c COLUMNS] [-m MODIFIER]
                  [FILE]

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      -n, --names           Display column names and indices from the input CSV
                            and exit.
      -c COLUMNS, --columns COLUMNS
                            A comma separated list of column indices or names to
                            be modified.
      -m MODIFIER, --modifier MODIFIER
                            If specified, the "sed" modifier to evaluate:
                            currently supports substitution (s/REGEX/REPL/FLAGS),
                            transliteration (y/SRC/DEST/FLAGS) and execution
                            (e/REGEX/COMMAND/FLAGS).


See also: :doc:`../common_arguments`.

Examples
========

Remove thousands-separators from the "Wage" column using the "s" (substitute) modifier::

    csvsed -c Wage -m 's/,//g' ../examples/csvsed.csv

Convert column "Status" to lower-case using the "y" (transliterate) modifier::

    csvsed -c Status -m 'y/a-z/A-Z/' ../examples/csvsed.csv

Square the "Age" column using the "e" (execute) modifier::

    csvsed -c Age -m 'e/^[0-9]+$/xargs -I {} echo "{}^2/" | bc/' ../examples/csvsed.csv