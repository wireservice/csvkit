==============================
Going elsewhere with your data
==============================

csvjson: going online
=====================

Very frequently one of the last steps in any data analysis is to get the data onto the web for display as a table, map or chart. CSV is rarely the ideal format for this. More often than not what you want is JSON and that's where :doc:`/scripts/csvjson` comes in. ``csvjson`` takes an input CSV and outputs neatly formatted JSON. For the sake of illustration, let's use ``csvcut`` and ``csvgrep`` to convert just a small slice of our data:

.. code-block:: bash

    csvcut -c county,item_name data.csv | csvgrep -c county -m "GREELEY" | csvjson --indent 4

.. code-block:: json

    [
        {
            "county": "GREELEY",
            "item_name": "RIFLE,7.62 MILLIMETER"
        },
        {
            "county": "GREELEY",
            "item_name": "RIFLE,7.62 MILLIMETER"
        },
        {
            "county": "GREELEY",
            "item_name": "RIFLE,7.62 MILLIMETER"
        }
    ]

A common usage of turning a CSV into a JSON file is for usage as a lookup table in the browser. This can be illustrated with the ACS data we looked at earlier, which contains a unique ``fips`` code for each county:

.. code-block:: bash

    csvjson --indent 4 --key fips acs2012_5yr_population.csv | head

.. code-block:: json

    {
        "31001": {
            "fips": "31001",
            "name": "Adams County, NE",
            "total_population": "31299",
            "margin_of_error": "0"
        },
        "31003": {
            "fips": "31003",
            "name": "Antelope County, NE",
            "...": "..."
        }
    }

For making maps, ``csvjson`` can also output GeoJSON, see its :doc:`/scripts/csvjson` for more details.

csvpy: going into code
======================

For the programmers out there, the command line is rarely as functional as just writing a little bit of code. :doc:`/scripts/csvpy` exists just to make a programmer's life easier. Invoking it simply launches a Python interactive terminal, with the data preloaded into a CSV reader:

.. code-block:: bash

    csvpy data.csv

.. code-block:: none

    Welcome! "data.csv" has been loaded in a reader object named "reader".
    >>> print len(list(reader))
    1037
    >>> quit()

In addition to being a time-saver, because this uses agate, the reader is Unicode aware.

csvformat: for legacy systems
=============================

It is a foundational principle of csvkit that it always outputs cleanly formatted CSV data. None of the normal csvkit tools can be forced to produce pipe or tab-delimited output, despite these being common formats. This principle is what allows the csvkit tools to chain together so easily and hopefully also reduces the amount of crummy, non-standard CSV files in the world. However, sometimes a legacy system just has to have a pipe-delimited file and it would be crazy to make you use another tool to create it. That's why we've got :doc:`/scripts/csvformat`.

Pipe-delimited:

.. code-block:: bash

    csvformat -D \| data.csv

Tab-delimited:

.. code-block:: bash

    csvformat -T data.csv

Quote every cell:

.. code-block:: bash

    csvformat -U 1 data.csv

Ampersand-delimited, dollar-signs for quotes, quote all strings, and asterisk for line endings:

.. code-block:: bash

    csvformat -D \& -Q \$ -U 2 -M \* data.csv

You get the picture.

Summing up
==========

Thus concludes the csvkit tutorial. At this point, I hope, you have a sense a breadth of possibilities these tools open up with a relatively small number of command-line tools. Of course, this tutorial has only scratched the surface of the available options, so remember to check the :doc:`/cli` documentation for each tool as well.

So armed, go forth and expand the empire of the king of tabular file formats.
