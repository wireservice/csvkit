========
csvstack
========

Description
===========

Stack up the rows from multiple CSV files, optionally adding a grouping value to each row::

    usage: csvstack [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                    [-p ESCAPECHAR] [-z MAXFIELDSIZE] [-e ENCODING] [-S] [-H] [-v]
                    [-l] [--zero] [-g GROUPS] [-n GROUP_NAME] [--filenames]
                    FILE [FILE ...]

    Stack up the rows from multiple CSV files, optionally adding a grouping value.

    positional arguments:
      FILE                  The CSV file(s) to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      -g GROUPS, --groups GROUPS
                            A comma-separated list of values to add as "grouping
                            factors", one for each CSV being stacked. These will
                            be added to the stacked CSV as a new column. You may
                            specify a name for the grouping column using the -n
                            flag.
      -n GROUP_NAME, --group-name GROUP_NAME
                            A name for the grouping column, e.g. "year". Only used
                            when also specifying -g.
      --filenames           Use the filename of each input file as its grouping
                            value. When specified, -g will be ignored.

See also: :doc:`../common_arguments`.

Examples
========

Contrived example: joining a set of homogoenous files for different years::

    csvstack -g 2009,2010 examples/realdata/FY09_EDU_Recipients_by_State.csv examples/realdata/Datagov_FY10_EDU_recp_by_State.csv
