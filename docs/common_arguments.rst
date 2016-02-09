=============================
Arguments common to all tools
=============================

All tools which accept CSV as input share a set of common command-line arguments::

  -d DELIMITER, --delimiter DELIMITER
                        Delimiting character of the input CSV file.
  -t, --tabs            Specifies that the input CSV file is delimited with
                        tabs. Overrides "-d".
  -q QUOTECHAR, --quotechar QUOTECHAR
                        Character used to quote strings in the input CSV file.
  -u {0,1,2,3}, --quoting {0,1,2,3}
                        Quoting style used in the input CSV file. 0 = Quote
                        Minimal, 1 = Quote All, 2 = Quote Non-numeric, 3 =
                        Quote None.
  -b, --no-doublequote  Whether or not double quotes are doubled in the input
                        CSV file.
  -p ESCAPECHAR, --escapechar ESCAPECHAR
                        Character used to escape the delimiter if --quoting 3
                        ("Quote None") is specified and to escape the
                        QUOTECHAR if --no-doublequote is not specified.
  -z MAXFIELDSIZE, --maxfieldsize MAXFIELDSIZE
                        Maximum length of a single field in the input CSV
                        file.
  -e ENCODING, --encoding ENCODING
                        Specify the encoding the input CSV file.
  -S, --skipinitialspace
                        Ignore whitespace immediately following the delimiter.
  -H, --no-header-row   Specifies that the input CSV file has no header row.
                        Will create default headers (A,B,C,...).
  -v, --verbose         Print detailed tracebacks when errors occur.
  -l, --linenumbers     Insert a column of line numbers at the front of the
                        output. Useful when piping to grep or as a simple
                        primary key.
  --zero                When interpreting or displaying column numbers, use
                        zero-based numbering instead of the default 1-based
                        numbering.

These arguments may be used to override csvkit's default "smart" parsing of CSV files. This is frequently necessary if the input file uses a particularly unusual style of quoting or is an encoding that is not compatible with utf-8. Not every command is supported by every tool, but the majority of them are.

Note that the output of csvkit's tools is always formatted with "default" formatting options. This means that when executing multiple csvkit commands (either with a pipe or via intermediary files) it is only ever necessary to specify formatting arguments the first time. (And doing so for subsequent commands will likely cause them to fail.)

