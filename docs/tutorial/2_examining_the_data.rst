==================
Examining the data
==================

csvstat: statistics without code
================================

In the previous section we saw how we could use :doc:`/scripts/csvlook` and :doc:`/scripts/csvcut` to view slices of our data. This is a good tool for exploring a dataset, but in practice we usually need to get the broadest possible view before we can start diving into specifics.

:doc:`/scripts/csvstat` is designed to give us just such a broad understanding of our data. Inspired by the ``summary()`` function from the computational statistics programming language `"R" <https://www.r-project.org/>`_, :doc:`/scripts/csvstat` will generate summary statistics for all the data in a CSV file.

Let's examine summary statistics for a few columns from our dataset. As we learned in the last section, we can use :doc:`/scripts/csvcut` and a pipe to pick out the columns we want:

.. code-block:: console

   $ csvcut -c county,acquisition_cost,ship_date data.csv | csvstat
     1. "county"

    Type of data:          Text
    Contains null values:  False
    Unique values:         35
    Longest value:         10 characters
    Most common values:    DOUGLAS (760x)
                           DAKOTA (42x)
                           CASS (37x)
                           HALL (23x)
                           LANCASTER (18x)

     2. "acquisition_cost"

    Type of data:          Number
    Contains null values:  False
    Unique values:         75
    Smallest value:        0
    Largest value:         412,000
    Sum:                   5,430,787.55
    Mean:                  5,242.073
    Median:                6,000
    StDev:                 13,368.078
    Most common values:    6,800 (304x)
                           10,747 (195x)
                           6,000 (105x)
                           499 (98x)
                           0 (81x)

     3. "ship_date"

    Type of data:          Date
    Contains null values:  False
    Unique values:         84
    Smallest value:        2006-03-07
    Largest value:         2014-01-30
    Most common values:    2013-04-25 (495x)
                           2013-04-26 (160x)
                           2008-05-20 (28x)
                           2012-04-16 (26x)
                           2006-11-17 (20x)

   Row count: 1036

:doc:`/scripts/csvstat` infers the type of data in each column and then performs basic statistics on it. The particular statistics computed depend on the type of the column (numbers, text, dates, etc).

In this example the first column, ``county`` was identified as type ``Text``. We see that there are ``35`` counties represented in the dataset and that ``DOUGLAS`` is far and away the most frequently occurring. A quick Google search shows that there are ``93`` counties in Nebraska, so we know that either not every county received equipment or that the data is incomplete. We can also find out that Douglas county contains Omaha, the state's largest city by far.

The ``acquisition_cost`` column is type ``Number``. We see that the largest individual cost was ``412000.0``. (Probably dollars, but let's not presume.) Total acquisition costs were ``5430787.55``.

Lastly, the ``ship_date`` column (type ``Date``) shows us that the earliest data is from ``2006`` and the latest from ``2014``. We may also note that an unusually large amount of equipment was shipped in April, 2013.

As a journalist, this quick glance at the data gave me a tremendous amount of information about the dataset. Although we have to be careful about assuming too much from this quick glance (always double-check the numbers mean what you think they mean!) it can be an invaluable way to familiarize yourself with a new dataset.

csvgrep: find the data you need
===============================

After reviewing the summary statistics you might wonder what equipment was received by a particular county. To get a simple answer to the question we can use :doc:`/scripts/csvgrep` to search for the state's name amongst the rows. Let's also use :doc:`/scripts/csvcut` to just look at the columns we care about and :doc:`/scripts/csvlook` to format the output:

.. code-block:: console

   $ csvcut -c county,item_name,total_cost data.csv | csvgrep -c county -m LANCASTER | csvlook
   | county    | item_name                      | total_cost |
   | --------- | ------------------------------ | ---------- |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | LIGHT ARMORED VEHICLE          |          0 |
   | LANCASTER | LIGHT ARMORED VEHICLE          |          0 |
   | LANCASTER | LIGHT ARMORED VEHICLE          |          0 |
   | LANCASTER | MINE RESISTANT VEHICLE         |    412,000 |
   | LANCASTER | IMAGE INTENSIFIER,NIGHT VISION |      6,800 |
   | LANCASTER | IMAGE INTENSIFIER,NIGHT VISION |      6,800 |
   | LANCASTER | IMAGE INTENSIFIER,NIGHT VISION |      6,800 |
   | LANCASTER | IMAGE INTENSIFIER,NIGHT VISION |      6,800 |

``LANCASTER`` county contains Lincoln, Nebraska, the capital of the state and its second-largest city. The ``-m`` flag means "match" and will find text anywhere in a given column--in this case the ``county`` column. For those who need a more powerful search you can also use ``-r`` to search for a regular expression.

csvsort: order matters
======================

Now let's use :doc:`/scripts/csvsort` to sort the rows by the ``total_cost`` column, in reverse (descending) order:

.. code-block:: console

   $ csvcut -c county,item_name,total_cost data.csv | csvgrep -c county -m LANCASTER | csvsort -c total_cost -r | csvlook
   | county    | item_name                      | total_cost |
   | --------- | ------------------------------ | ---------- |
   | LANCASTER | MINE RESISTANT VEHICLE         |    412,000 |
   | LANCASTER | IMAGE INTENSIFIER,NIGHT VISION |      6,800 |
   | LANCASTER | IMAGE INTENSIFIER,NIGHT VISION |      6,800 |
   | LANCASTER | IMAGE INTENSIFIER,NIGHT VISION |      6,800 |
   | LANCASTER | IMAGE INTENSIFIER,NIGHT VISION |      6,800 |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | RIFLE,5.56 MILLIMETER          |        120 |
   | LANCASTER | LIGHT ARMORED VEHICLE          |          0 |
   | LANCASTER | LIGHT ARMORED VEHICLE          |          0 |
   | LANCASTER | LIGHT ARMORED VEHICLE          |          0 |

Two interesting things should jump out about this sorted data: that ``LANCASTER`` county got a very expensive ``MINE RESISTANT VEHICLE`` and that it also go three other ``LIGHT ARMORED VEHICLE``.

What commands would you use to figure out if other counties also received large numbers of vehicles?

Summing up
==========

At this point you should be able to use csvkit to investigate the basic properties of a dataset. If you understand this section, you should be ready to move onto :doc:`3_power_tools`.
