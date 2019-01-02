=============================
Arguments common to all tools
=============================

csvkit's tools share a set of common command-line arguments. Not every argument is supported by every tool, so please check which are supported by the tool you are using with the :code:`--help` flag::

  -d DELIMITER, --delimiter DELIMITER
                        Delimiting character of the input CSV file.
  -t, --tabs            Specify that the input CSV file is delimited with
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
                        QUOTECHAR if --no-doublequote is specified.
  -z FIELD_SIZE_LIMIT, --maxfieldsize FIELD_SIZE_LIMIT
                        Maximum length of a single field in the input CSV
                        file.
  -e ENCODING, --encoding ENCODING
                        Specify the encoding of the input CSV file.
  -L LOCALE, --locale LOCALE
                        Specify the locale (en_US) of any formatted numbers.
  -S, --skipinitialspace
                        Ignore whitespace immediately following the delimiter.
  --blanks              Do not coerce empty, "na", "n/a", "none", "null", "."
                        strings to NULL values.
  --date-format DATE_FORMAT
                        Specify a strptime date format string like "%m/%d/%Y".
  --datetime-format DATETIME_FORMAT
                        Specify a strptime datetime format string like
                        "%m/%d/%Y %I:%M %p".
  -H, --no-header-row   Specify that the input CSV file has no header row.
                        Will create default headers (a,b,c,...).
  -K SKIP_LINES, --skip-lines SKIP_LINES
                        Specify the number of initial lines to skip before the
                        header row (e.g. comments, copyright notices, empty
                        rows).
  -v, --verbose         Print detailed tracebacks when errors occur.
  -l, --linenumbers     Insert a column of line numbers at the front of the
                        output. Useful when piping to grep or as a simple
                        primary key.
  --zero                When interpreting or displaying column numbers, use
                        zero-based numbering instead of the default 1-based
                        numbering.
  -V, --version         Display version information and exit.

These arguments can be used to override csvkit's default "smart" parsing of CSV files. This may be necessary, for example, if the input file uses a particularly unusual quoting style or has an encoding that is incompatible with UTF-8.

For example, to disable CSV sniffing, set :code:`--snifflimit 0` and then, if necessary, set the :code:`--delimiter` and :code:`--quotechar` options yourself. To disable type inference, add the :code:`--no-inference` flag.

The output of csvkit's tools is always formatted with "default" formatting options. This means that when executing multiple csvkit commands (either with a pipe or through intermediary files) it is only ever necessary to specify these arguments the first time (and doing so for subsequent commands will likely cause them to fail).

See the documentation of :doc:`/scripts/csvclean` for a description of the default formatting options.
