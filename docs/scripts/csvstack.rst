========
csvstack
========

Description
===========

Stack up the rows from multiple CSV files, optionally adding a grouping value to each row::

    usage: csvstack [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                    [-p` ESCAPECHAR] [-e ENCODING] [-g GROUPS] [-n GROUP_NAME]
                    FILES [FILES ...]

    Stack up the rows from multiple CSV files, optionally adding a grouping value.

    positional arguments:
      FILES

    optional arguments:
      -h, --help            show this help message and exit
      -g GROUPS, --groups GROUPS
                            A comma-seperated list of values to add as "grouping
                            factors", one for each CSV being stacked. These will
                            be added to the stacked CSV as a new column. You may
                            specify a name for the grouping column using the -n
                            flag.
      -n GROUP_NAME, --group-name GROUP_NAME
                            A name for the grouping column, e.g. "year". Only used
                            when also specifying -g.

Also see: :doc:`common_arguments`.

Examples
========

Contrived example: joining a set of homogoenous files for different years::

    $ csvstack -g 1984,1985 -n year examples/testfixed_converted.csv examples/testfixed_converted.csv
