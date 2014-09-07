===========
Power tools
===========

csvjoin: merging related data
=============================

One of the most common operations that we need to perform on data is "join" it to another, related dataset. For instance, given data about equipment supplied to counties in Nebraska, one might reasonably want to compare those numbers to the population of each county. :doc:`/scripts/csvjoin` allows us to take two those two datasets (equipment and population) and merge them, much like you might do with a SQL JOIN query. In order to demonstrate this, let's grab our second dataset::

    $ curl -L -O https://github.com/onyxfish/csvkit/raw/master/examples/realdata/acs2012_5yr_population.csv

Let's see what's in there::

    $ csvstat acs2012_5yr_population.csv
      1. fips
            <type 'int'>
            Nulls: False
            Min: 31001
            Max: 31185
            Sum: 2891649
            Mean: 31093.0
            Median: 31093
            Standard Deviation: 53.6904709112
            Unique values: 93
      2. name
            <type 'unicode'>
            Nulls: False
            Unique values: 93
            Max length: 23
      3. total_population
            <type 'int'>
            Nulls: False
            Min: 348
            Max: 518271
            Sum: 1827306
            Mean: 19648.4516129
            Median: 6294
            Standard Deviation: 62164.0702096
            Unique values: 93
      4. margin_of_error
            <type 'int'>
            Nulls: False
            Min: 0
            Max: 115
            Sum: 1800
            Mean: 19.3548387097
            Median: 0
            Standard Deviation: 37.6927719494
            Unique values: 15
            5 most frequent values:
                    0:      73
                    115:    2
                    114:    2
                    99:     2
                    73:     2

    Row count: 93

As you can see, this data file contains population estimates for each county in Nebraska from the 2012 5-year ACS estimates. This data was retrieved from `Census Reporter <http://censusreporter.org/>`_ and reformatted slightly for this example. Let's join it to our equipment data::

    $ csvjoin -c fips data.csv acs2012_5yr_population.csv > joined.csv

Since both files contain a fips column, we can use that to join the two. In our output you should see the population data appended at the end of each row of data. Let's combine this with what we've learned before to answer the question "What was the smallest county to receive equipment and what did they receive?"::

    $ csvcut -c county,item_name,total_population joined.csv | csvsort -c total_population | csvlook | head
    |-------------+----------------------------------------------------------------+-------------------|
    |  county     | item_name                                                      | total_population  |
    |-------------+----------------------------------------------------------------+-------------------|
    |  MCPHERSON  | RIFLE,5.56 MILLIMETER                                          | 348               |
    |  WHEELER    | RIFLE,5.56 MILLIMETER                                          | 725               |
    |  GREELEY    | RIFLE,7.62 MILLIMETER                                          | 2515              |
    |  GREELEY    | RIFLE,7.62 MILLIMETER                                          | 2515              |
    |  GREELEY    | RIFLE,7.62 MILLIMETER                                          | 2515              |
    |  NANCE      | RIFLE,5.56 MILLIMETER                                          | 3730              |
    |  NANCE      | RIFLE,7.62 MILLIMETER                                          | 3730              |

Two counties with fewer than one-thousand residents were the recipients of 5.56 millimeter assault rifles.

csvstack: combining subsets
===========================

TODO: Add more states...

csvsql: ultimate power
======================

Sometimes (almost always), the command line isn't enough. It would be crazy to try to do all your analysis using command line tools. Often times, the correct tool for data analysis is SQL. :doc:`/scripts/csvsql` is a bridge that eases migrating your data from a CSV file into a SQL database. For smaller datasets it can also leverage sqlite to allow execution of ad hoc SQL queries without ever touching a database.

TODO

Summing up
==========

TODO

Up next: :doc:`4_going_elsewhere`
