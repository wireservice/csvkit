===========
Power tools
===========

csvjoin: merging related data
=============================

One of the most common operations that we need to perform on data is "joining" it to other, related data. For instance, given a dataset about equipment supplied to counties in Nebraska, one might reasonably want to merge that with a dataset containing the population of each county. :doc:`/scripts/csvjoin` allows us to take those two datasets (equipment and population) and merge them, much like you might do with a SQL ``JOIN`` query. In order to demonstrate this, let's grab a second dataset:

.. code-block:: bash

   curl -L -O https://raw.githubusercontent.com/wireservice/csvkit/master/examples/realdata/acs2012_5yr_population.csv

Now let's see what's in there:

.. code-block:: console

   $ csvstat acs2012_5yr_population.csv
     1. "fips"

    Type of data:          Number
    Contains null values:  False
    Unique values:         93
    Smallest value:        31,001
    Largest value:         31,185
    Sum:                   2,891,649
    Mean:                  31,093
    Median:                31,093
    StDev:                 53.981
    Most common values:    31,001 (1x)
                           31,003 (1x)
                           31,005 (1x)
                           31,007 (1x)
                           31,009 (1x)

     2. "name"

    Type of data:          Text
    Contains null values:  False
    Unique values:         93
    Longest value:         23 characters
    Most common values:    Adams County, NE (1x)
                           Antelope County, NE (1x)
                           Arthur County, NE (1x)
                           Banner County, NE (1x)
                           Blaine County, NE (1x)

     3. "total_population"

    Type of data:          Number
    Contains null values:  False
    Unique values:         93
    Smallest value:        348
    Largest value:         518,271
    Sum:                   1,827,306
    Mean:                  19,648.452
    Median:                6,294
    StDev:                 62,501.005
    Most common values:    31,299 (1x)
                           6,655 (1x)
                           490 (1x)
                           778 (1x)
                           584 (1x)

     4. "margin_of_error"

    Type of data:          Number
    Contains null values:  False
    Unique values:         15
    Smallest value:        0
    Largest value:         115
    Sum:                   1,800
    Mean:                  19.355
    Median:                0
    StDev:                 37.897
    Most common values:    0 (73x)
                           73 (2x)
                           114 (2x)
                           97 (2x)
                           99 (2x)

   Row count: 93

As you can see, this data file contains population estimates for each county in Nebraska from the 2012 5-year ACS estimates. This data was retrieved from `Census Reporter <https://censusreporter.org/>`_ and reformatted slightly for this example. Let's join it to our equipment data:

.. code-block:: bash

   csvjoin -c fips data.csv acs2012_5yr_population.csv > joined.csv

Since both files contain a fips column, we can use that to join the two. In our output you should see the population data appended at the end of each row of data. Let's combine this with what we've learned before to answer the question "What was the lowest population county to receive equipment?":

.. code-block:: console

   $ csvcut -c county,item_name,total_population joined.csv | csvsort -c total_population | csvlook | head
   | county     | item_name                                                      | total_population |
   | ---------- | -------------------------------------------------------------- | ---------------- |
   | MCPHERSON  | RIFLE,5.56 MILLIMETER                                          |              348 |
   | WHEELER    | RIFLE,5.56 MILLIMETER                                          |              725 |
   | GREELEY    | RIFLE,7.62 MILLIMETER                                          |            2,515 |
   | GREELEY    | RIFLE,7.62 MILLIMETER                                          |            2,515 |
   | GREELEY    | RIFLE,7.62 MILLIMETER                                          |            2,515 |
   | NANCE      | RIFLE,5.56 MILLIMETER                                          |            3,730 |
   | NANCE      | RIFLE,7.62 MILLIMETER                                          |            3,730 |
   | NANCE      | RIFLE,7.62 MILLIMETER                                          |            3,730 |

Two counties with fewer than one-thousand residents were the recipients of 5.56 millimeter assault rifles. This simple example demonstrates the power of joining datasets. Although SQL will always be a more flexible option, :doc:`/scripts/csvjoin` will often get you where you need to go faster.

csvstack: combining subsets
===========================

Frequently large datasets are distributed in many small files. At some point you will probably want to merge those files for bulk analysis. :doc:`/scripts/csvstack` allows you to "stack" the rows from CSV files with the same columns (and identical column names). To demonstrate, let's imagine we've decided that Nebraska and Kansas form a "region" and that it would be useful to analyze them in a single dataset. Let's grab the Kansas data:

.. code-block:: bash

   curl -L -O https://raw.githubusercontent.com/wireservice/csvkit/master/examples/realdata/ks_1033_data.csv

Back in :doc:`1_getting_started`, we had used in2csv to convert our Nebraska data from XLSX to CSV. However, we named our output `data.csv` for simplicity at the time. Now that we are going to be stacking multiple states, we should re-convert our Nebraska data using a file naming convention matching our Kansas data:

.. code-block:: bash

   in2csv ne_1033_data.xlsx > ne_1033_data.csv

Now let's stack these two data files:

.. code-block:: bash

   csvstack ne_1033_data.csv ks_1033_data.csv > region.csv

Using csvstat we can see that our ``region.csv`` contains both datasets:

.. code-block:: console

   $ csvstat -c state,acquisition_cost region.csv
     1. "state"

    Type of data:          Text
    Contains null values:  False
    Unique values:         2
    Longest value:         2 characters
    Most common values:    KS (1575x)
                           NE (1036x)

     8. "acquisition_cost"

    Type of data:          Number
    Contains null values:  False
    Unique values:         127
    Smallest value:        0
    Largest value:         658,000
    Sum:                   9,440,445.91
    Mean:                  3,615.644
    Median:                138
    StDev:                 23,730.631
    Most common values:    120 (649x)
                           499 (449x)
                           138 (311x)
                           6,800 (304x)
                           58.71 (218x)

   Row count: 2611

If you supply the :code:`-g` flag then :doc:`/scripts/csvstack` can also add a "grouping column" to each row, so that you can tell which file each row came from. In this case we don't need this, but you can imagine a situation in which instead of having a ``county`` column each of this datasets had simply been named ``nebraska.csv`` and ``kansas.csv``. In that case, using a grouping column would prevent us from losing information when we stacked them.

csvsql and sql2csv: ultimate power
==================================

Sometimes (almost always), the command-line isn't enough. It would be crazy to try to do all your analysis using command-line tools. Often times, the correct tool for data analysis is SQL. :doc:`/scripts/csvsql` and :doc:`/scripts/sql2csv` form a bridge that eases migrating your data into and out of a SQL database. For smaller datasets :doc:`/scripts/csvsql` can also leverage `sqlite <https://www.sqlite.org/>`_ to allow execution of ad hoc SQL queries without ever touching a database.

By default, :doc:`/scripts/csvsql` will generate a create table statement for your data. You can specify what sort of database you are using with the ``-i`` flag:

.. code-block:: bash

   csvsql -i sqlite joined.csv

.. code-block:: sql

   CREATE TABLE joined (
       state VARCHAR NOT NULL, 
       county VARCHAR NOT NULL, 
       fips FLOAT NOT NULL, 
       nsn VARCHAR NOT NULL, 
       item_name VARCHAR, 
       quantity FLOAT NOT NULL, 
       ui VARCHAR NOT NULL, 
       acquisition_cost FLOAT NOT NULL, 
       total_cost FLOAT NOT NULL, 
       ship_date DATE NOT NULL, 
       federal_supply_category FLOAT NOT NULL, 
       federal_supply_category_name VARCHAR NOT NULL, 
       federal_supply_class FLOAT NOT NULL, 
       federal_supply_class_name VARCHAR NOT NULL, 
       name VARCHAR NOT NULL, 
       total_population FLOAT NOT NULL, 
       margin_of_error FLOAT NOT NULL
   );

Here we have the sqlite "create table" statement for our joined data. You'll see that, like :doc:`/scripts/csvstat`, :doc:`/scripts/csvsql` has done its best to infer the column types.

Often you won't care about storing the SQL statements locally. You can also use :doc:`/scripts/csvsql` to create the table directly in the database on your local machine. If you add the :code:`--insert` option the data will also be imported:

.. code-block:: bash

   csvsql --db sqlite:///leso.db --insert joined.csv

How can we check that our data was imported successfully? We could use the sqlite command-line interface, but rather than worry about the specifics of another tool, we can also use :doc:`/scripts/sql2csv`:

.. code-block:: bash

   sql2csv --db sqlite:///leso.db --query "select * from joined"

Note that the :code:`--query` parameter to :doc:`/scripts/sql2csv` accepts any SQL query. For example, to export Douglas county from the ``joined`` table from our sqlite database, we would run:

.. code-block:: bash

   sql2csv --db sqlite:///leso.db --query "select * from joined where county='DOUGLAS';" > douglas.csv

Sometimes, if you will only be running a single query, even constructing the database is a waste of time. For that case, you can actually skip the database entirely and :doc:`/scripts/csvsql` will create one in memory for you:

.. code-block:: bash

   csvsql --query "select county,item_name from joined where quantity > 5;" joined.csv | csvlook

SQL queries directly on CSVs! Keep in mind when using this that you are loading the entire dataset into an in-memory SQLite database, so it is likely to be very slow for large datasets.

Summing up
==========

:doc:`/scripts/csvjoin`, :doc:`/scripts/csvstack`, :doc:`/scripts/csvsql` and :doc:`/scripts/sql2csv` represent the power tools of csvkit. Using these tools can vastly simplify processes that would otherwise require moving data between other systems. But what about cases where these tools still don't cut it? What if you need to move your data onto the web or into a legacy database system? We've got a few solutions for those problems in our final section, :doc:`4_going_elsewhere`.
