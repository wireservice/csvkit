=======
csvjson
=======

Description
===========

Converts a CSV file into JSON::

    usage: csvjson [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                   [-p ESCAPECHAR] [-e ENCODING] [-v] [-l] [-i INDENT] [-k KEY]
                   [FILE]

    Convert a CSV file into JSON.

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -i INDENT, --indent INDENT
                            Indent the output JSON this many spaces. Disabled by
                            default.
      -k KEY, --key KEY     Output JSON as an array of objects keyed by a given
                            column, KEY, rather than as a list. All values in the
                            column must be unique.


Also see: :doc:`common_arguments`.

Examples
========

Convert veteran's education dataset to JSON keyed by state abbreviation::

    $ csvjson -k "State Abbreviate" -i 4 examples/realdata/FY09_EDU_Recipients_by_State.csv

Results in a JSON document like::

    {
        [...]
        "WA": 
        {
            "": "",
             "Code": "53",
             "Reserve Educational Assistance Program": "549",
             "Dependents' Educational Assistance": "2,192",
             "Montgomery GI Bill-Active Duty": "7,969",
             "State Name": "WASHINGTON",
             "Montgomery GI Bill- Selective Reserve": "769",
             "State Abbreviate": "WA",
             "Post-Vietnam Era Veteran's Educational Assistance Program": "13",
             "TOTAL": "11,492"
        },
        [...]
    }

