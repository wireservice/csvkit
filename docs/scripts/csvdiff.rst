=======
csvdiff
=======

Description
===========

Compare two CSV tables, and produce another CSV table that summarizes their differences.::

    usage: csvdiff [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                   [-p ESCAPECHAR] [-z MAXFIELDSIZE] [-e ENCODING] [-S] [-v] [-l]
                   [--zero] [-c COLUMNS] [--color]
                   [FILE [FILE ...]]
    
    Compare CSV files. Like unix "diff" command, but for tabular data.
    
    positional arguments:
      FILE                  The CSV files to operate on.
    
    optional arguments:
      -h, --help            show this help message and exit
      -c COLUMNS, --columns COLUMNS
                            The column name(s) to use for comparison. Should be
                            either one name or a comma-separated list of names.
                            May also be left unspecified, in which case we'll
                            guess something plausible.
      --color               Decorate output with colors and glyphs.
    
    Note that the diff operation requires reading all files into memory. Don't try
    this on very large files.


See also: :doc:`../common_arguments`.

Examples
========

::

    csvdiff file1.csv file2.csv

This command says you have two files to compare, file1.csv and file2.csv. 
A typical output will look like this:

.. raw:: html

    <p style="font-family: monospace;">
    <span style="font-weight:bold">@@</span>&nbsp;,<span style="font-weight:bold">bridge</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;,<span style="font-weight:bold">designer</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;,<span style="font-weight:bold">length</span><br/>
    &nbsp;&nbsp;&nbsp;,Brooklyn&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;,"J.&nbsp;A.&nbsp;Roebling"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;,1595<br/>
    <span style="color:green"></span><span style="color:green;font-weight:bold">+++</span>,<span style="color:green"></span><span style="color:green;font-weight:bold">Manhattan</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;,"<span style="color:green"></span><span style="color:green;font-weight:bold">G.&nbsp;Lindenthal</span>"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;,<span style="color:green"></span><span style="color:green;font-weight:bold">1470</span><br/>
    <span style="color:red"></span><span style="color:red;font-weight:bold"></span><span style="color:blue;font-weight:bold"></span><span style="color:blue;font-weight:bold">→</span><span style="color:green;font-weight:bold"></span><span style="color:green;font-weight:bold"></span>&nbsp;&nbsp;,Williamsburg&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;,"<span style="color:red"></span><span style="color:red;font-weight:bold">D.&nbsp;Duck</span><span style="color:blue;font-weight:bold"></span><span style="color:blue;font-weight:bold">→</span><span style="color:green;font-weight:bold"></span><span style="color:green;font-weight:bold">L.&nbsp;L.&nbsp;Buck</span>"&nbsp;,1600<br/>
    &nbsp;&nbsp;&nbsp;,Queensborough&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;,"Palmer&nbsp;&&nbsp;Hornbostel",1182<br/>
    ...,...&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;,...&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;,...<br/>
    &nbsp;&nbsp;&nbsp;,"George&nbsp;Washington","O.&nbsp;H.&nbsp;Ammann"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;,3500<br/>
    <span style="color:red"></span><span style="color:red;font-weight:bold">---</span>,<span style="color:red"></span><span style="color:red;font-weight:bold">Spamspan</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;,"<span style="color:red"></span><span style="color:red;font-weight:bold">S.&nbsp;Spamington</span>"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;,<span style="color:red"></span><span style="color:red;font-weight:bold">10000</span>
   </p>

See http://dataprotocols.org/tabular-diff-format/ for information on the diff format. Color highlighting will by default only activate when the result is being shown on a console.
