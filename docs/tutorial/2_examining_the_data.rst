==================
Examining the data
==================

csvstat: statistics without code
================================

In the previous section we saw how we could use ``csvlook`` and ``csvcut`` to peek at slices of our data. This is a good starting place for diving into a dataset, but in practice we usually want to get the widest possible view before we start diving into specifics.

:doc:`/scripts/csvstat` is designed to give us just such a broad picture of our data. It is inspired by the summary() function from the computational statistics programming language `"R" <http://www.r-project.org/>`_.

Let's examine summary statistics for some selected columns from our data (remember you can use ``csvcut -n data.csv`` to see the columns in the data)::

    $ csvcut -c county,acquisition_cost,ship_date data.csv | csvstat
      1. county
            <type 'unicode'>
            Nulls: False
            Unique values: 35
            5 most frequent values:
                    DOUGLAS:        760
                    DAKOTA: 42
                    CASS:   37
                    HALL:   23
                    LANCASTER:      18
            Max length: 10
      2. acquisition_cost
            <type 'float'>
            Nulls: False
            Min: 0.0
            Max: 412000.0
            Sum: 5438254.0
            Mean: 5249.27992278
            Median: 6000.0
            Standard Deviation: 13360.1600088
            Unique values: 75
            5 most frequent values:
                    6800.0: 304
                    10747.0:        195
                    6000.0: 105
                    499.0:  98
                    0.0:    81
      3. ship_date
            <type 'datetime.date'>
            Nulls: False
            Min: 1984-12-31
            Max: 2054-12-31
            Unique values: 84
            5 most frequent values:
                    2013-04-25:     495
                    2013-04-26:     160
                    2008-05-20:     28
                    2012-04-16:     26
                    2006-11-17:     20

    Row count: 1036

``csvstat`` algorithmically infers the type of each column in the data and then performs basic statistics on it. The particular statistics computed depend on the type of the column.

In this example the first column, ``county`` was identified as type "unicode" (text). We see that there are ``35`` counties represented in the dataset and that ``DOUGLAS`` is far and away the most frequently occuring. A quick Google search shows that there are ``93`` counties in Nebraska, so we know that either not every county received equipment or that the data is incomplete. We can also find out that Douglas county contains Omaha, the state's largest city by far.

The ``acquisition_cost`` column is type "float" (number including a decimal). We see that the largest individual cost was ``412,000``. (Probably dollars, but let's not presume.) Total acquisition costs were ``5,438,254``. 

Lastly, the ``ship_date`` column shows us that the earliest data is from ``1984`` and the latest from ``2054``. From this we know that there is invalid data for at least one value, since presumably the equipment being shipped does not include time travel devices. We may also note that an unusually large amount of equipment was shipped in April, 2013. 

As a journalist, this quick glance at the data gave me a tremendous amount of information about the dataset. Although we have to be careful about assuming to much from this quick glance (always double-check the numbers!) it can be an invaluable way to familiarize yourself with a new dataset.

csvgrep: find the data you need
===============================

After reviewing the summary statistics you might wonder what equipment was received by a particular county. To get a simple answer to the question we can use :doc:`/scripts/csvgrep` to search for the state's name amongst the rows. Let's also use ``csvcut`` to just look at the columns we care about and ``csvlook`` to format the output::

    $ csvcut -c county,item_name,total_cost data.csv | csvgrep -c county -m LANCASTER | csvlook
    |------------+--------------------------------+-------------|
    |  county    | item_name                      | total_cost  |
    |------------+--------------------------------+-------------|
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | LIGHT ARMORED VEHICLE          | 0           |
    |  LANCASTER | LIGHT ARMORED VEHICLE          | 0           |
    |  LANCASTER | LIGHT ARMORED VEHICLE          | 0           |
    |  LANCASTER | MINE RESISTANT VEHICLE         | 412000      |
    |  LANCASTER | IMAGE INTENSIFIER,NIGHT VISION | 6800        |
    |  LANCASTER | IMAGE INTENSIFIER,NIGHT VISION | 6800        |
    |  LANCASTER | IMAGE INTENSIFIER,NIGHT VISION | 6800        |
    |  LANCASTER | IMAGE INTENSIFIER,NIGHT VISION | 6800        |
    |------------+--------------------------------+-------------|

``LANCASTER`` county contains Lincoln, Nebraska, the capital of the state and it's second-largest city. The ``-m`` flag means "match" and will find text anywhere in a given column--in this case the ``county`` column. For those who need a more powerful search you can also use ``-r`` to search for a regular expression.

csvsort: order matters
======================

Now let's use :doc:`/scripts/csvsort` to sort the rows by the ``total_cost`` column, in reverse (descending) order::

    $ csvcut -c county,item_name,total_cost data.csv | csvgrep -c county -m LANCASTER | csvsort -c total_cost -r | csvlook
    |------------+--------------------------------+-------------|
    |  county    | item_name                      | total_cost  |
    |------------+--------------------------------+-------------|
    |  LANCASTER | MINE RESISTANT VEHICLE         | 412000      |
    |  LANCASTER | IMAGE INTENSIFIER,NIGHT VISION | 6800        |
    |  LANCASTER | IMAGE INTENSIFIER,NIGHT VISION | 6800        |
    |  LANCASTER | IMAGE INTENSIFIER,NIGHT VISION | 6800        |
    |  LANCASTER | IMAGE INTENSIFIER,NIGHT VISION | 6800        |
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | RIFLE,5.56 MILLIMETER          | 120         |
    |  LANCASTER | LIGHT ARMORED VEHICLE          | 0           |
    |  LANCASTER | LIGHT ARMORED VEHICLE          | 0           |
    |  LANCASTER | LIGHT ARMORED VEHICLE          | 0           |
    |------------+--------------------------------+-------------|

Two interesting things should jump out about this sorted data: that ``LANCASTER`` county got a very expensive ``MINE RESISTANT VEHICLE`` and that it also go three other ``LIGHT ARMORED VEHICLE``.

What commands would you use to figure out if other counties also recieved large numbers of vehicles?

Summing up
==========

At this point you should be able to use csvkit to investigate the basic properties of a dataset. If you understand this section, you should be ready to move onto :doc:`3_power_tools`. 

