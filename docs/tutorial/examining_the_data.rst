==================
Examining the data
==================

Cutting up the data with csvcut
===============================

Now let's start investigating this dataset. The first thing we might want to know is what columns are included. To figure that out let's use :doc:`/scripts/csvcut`::

    $ csvcut -n 2009.csv
      1: State Name
      2: State Abbreviate
      3: Code
      4: Montgomery GI Bill-Active Duty
      5: Montgomery GI Bill- Selective Reserve
      6: Dependents' Educational Assistance
      7: Reserve Educational Assistance Program
      8: Post-Vietnam Era Veteran's Educational Assistance Program
      9: TOTAL
     10: 

``csvcut`` is the beating heart of csvkit and was the original inspiration for building the rest of the tools. However, in this case we aren't using its full power. When the -n flag is specified, ``csvcut`` simply prints the column numbers and names and exits. We'll see the rest of its capabilities shortly.

This tells us a few things about the dataset, including that the final column doesn't have a name. However, it doesn't tell you anything about what sort of data is in each column. Let's try peeking at a couple columns to try to figure that out::

    $ csvcut -c 2,3 2009.csv | head -n 5
    State Name,Code
    AL,01
    AK,02
    AZ,04
    AR,05

Now we see the power of ``csvcut``. Using the -c flag we are able to specify columns we want to extract from the input. We also use Unix utility ``head`` to look at just the first five rows of output. From the look of things the "Code" column is a identifier that is unique to each state. It also appears that the dataset is alphabetical by state.

Let's try one more way of using csvcut::

    $ csvcut -c "TOTAL" 2009.csv | sort -n
    ""
    "10,085"
    "1,084"
    "1,117"
    "1,145"
    [...]

As you can see we can identify a column by its number *or* its name. We are also showing how, in theory we might pipe the output to sort and have the values sorted, however, two things are preventing this from working correctly:

* the numbers have commas in them, which messes up the ordering
* the output of ``csvcut`` is itself in CSV format, and the column is being quoted because of the commas in the numbers

Statistics on demand with csvstat
=================================

Fortunantely, there is a much better way to do this. Another utility included with csvkit is :doc:`/scripts/csvstat`, which mimics the summary() function from the computational statistics programming language `"R" <http://www.r-project.org/>`_.

Let's use what we learned in the previous section to look at just a slice of the data::

    $ csvcut -c 1,4,9,10 2009.csv | csvstat 
      1. State Name
        <type 'unicode'>
        Nulls: Yes
        Unique values: 53
        Max length: 17
        Samples: "FLORIDA", "IDAHO", "ARIZONA", "OHIO", "IOWA"
      2. Montgomery GI Bill-Active Duty
        <type 'int'>
        Nulls: Yes
        Min: 435
        Max: 34942
        Mean: 6263
        Median: 3548.0
        Unique values: 53
      3. TOTAL
        <type 'int'>
        Nulls: Yes
        Min: 768
        Max: 46897
        Mean: 9748
        Median: 6520.0
        Unique values: 53
      4. 
	    Empty column

Like ``csvcut``, ``csvstat`` lists columns with their numbers (in this case the column numbers are those of the CSV file *output* by ``csvcut``). However, ``csvstat`` also performs type inference on the columns and computes relevant statistics based on their types. In this case we have a *unicode* column (internally csvkit uses unicode exclusively to represent text), and two *int* (integer) columns. For the unicode column we know it contains nulls (blanks), that it has 53 unique values, that the longest one is 17 characters, and we also have five examples of data from that column.

From the statistics on the integer columns we can see that the median number of indviduals exercising VA benefits across the states is 6520, of which 3548 is the median number exercising the GI Bill while on active duty. 

We also see that the final column of the original CSV not only lacks a header, but is entirely empty.

If this dataset had included a column of dates or times, ``csvstat`` would have displayed the range and other details relevant to time-sequences. 

Searching for rows with grep
============================

After reviewing the summary statistics you might wonder where your home state falls in the order. To get a simple answer to the question we can use the Unix utility ``grep`` to search for the state's name amongst the rows. Let's also use csvcut to just look at the columns we care about::

    $ csvcut -c 1,"TOTAL" 2009.csv | grep ILLINOIS
    ILLINOIS,"21,964"

So Illinois has well above the median number of individuals exercising their VA benefits. Note that one must exercise caution when using ``grep`` in this way. The word "ILLINOIS" could have appeared in any column, or even in a header, and those rows would have been included as well.

For more on ``grep`` and other Unix utilities, see :doc:`/scripts/unix_tools`.

Normalizing data with in2csv
============================

What if we wanted to know exactly where Illinois ranks? In order to properly sort the data we need to remove those extraneous commas from the numbers. :doc:`/scripts/in2csv` is a utility for converting other data formats into CSV, however, it can also be used to standardize the format of an existing CSV. In this case we can use it to eliminate the commas which prevent us from sorting the counts in our table.

*(Note: In the next few sections we will repeat some commands to show how you can build up a complex operation as a sequence of simple ones.)*::

    $ in2csv 2009.csv | head -n 5
    State Name,State Abbreviate,Code,Montgomery GI Bill-Active Duty,Montgomery GI Bill- Selective Reserve,Dependents' Educational Assistance,Reserve Educational Assistance Program,Post-Vietnam Era Veteran's Educational Assistance Program,TOTAL,
    ALABAMA,AL,01,6718,1728,2703,1269,8,12426,
    ALASKA,AK,02,776,154,166,60,2,1158,
    ARIZONA,AZ,04,26822,2005,3137,2011,11,33986,
    ARKANSAS,AR,05,2061,988,1575,886,3,5513,

We can see that ``in2csv`` is stripping commas from integers and eliminating extraneous quoting. Its also worth noting that it correctly preserves the leading zeroes in column three.

Reading through data with csvlook and less
==========================================

That last block of terminal output is very difficult to read due to the columns not lining up correctly. In general this problem makes CSV somewhat difficult to work with in the terminal. In order to mitigate this problem we can use :doc:`/scripts/csvlook` to display the data in a fixed-width table. Let's try it with a handful of columns::

    $ in2csv 2009.csv | csvcut -c 1,2,3,4 | csvlook
    ----------------------------------------------------------------------------------
    |  State Name        | State Abbreviate | Code | Montgomery GI Bill-Active Duty  |
    ----------------------------------------------------------------------------------
    |  ALABAMA           | AL               | 01   | 6718                            |
    |  ALASKA            | AK               | 02   | 776                             |
    |  ARIZONA           | AZ               | 04   | 26822                           |
    |  ARKANSAS          | AR               | 05   | 2061                            |
    [...]

*Hint: If your table doesn't render like this one, try making you terminal window wider.*

Isn't that better? You may still find it annoying it to have the entire contents of the table get dumped to your terminal window. To better manage the output try piping it to ``less`` or, if you're just glancing at it, ``more``.

Flipping column order with csvcut
=================================

Returning for a moment to ``csvcut``, we can use its column selection logic as a powertool for reordering columns. Let's pare back the number of columns and make the column we want to sort on first::

    $ in2csv 2009.csv | csvcut -c 9,1 | head -n 5
    TOTAL,State Name
    12426,ALABAMA
    1158,ALASKA
    33986,ARIZONA
    5513,ARKANSAS

Sorting with sort
=================

Now that the column we want to sort by is first we can use the Unix utility ``sort`` to numerically sort the rows::

    $ in2csv 2009.csv | csvcut -c 9,1 --skipheader | sort -n -r | head -n 5
    46897,CALIFORNIA
    40402,TEXAS
    36394,FLORIDA
    33986,ARIZONA
    21964,ILLINOIS

The -n argument tells ``sort`` to sort numerically and the -r tells it to sort in descending order. In this case we have also updated csvcut to use the --skipheader option, which prevents the header from being output, thus keeping it from inteferring with the sorting.

We can now see that Illinois ranks fifth for individuals claiming VA benefits, behind mostly larger states, although Arizona is a surprising name to appear in the top five, given its relative size. If we were to join this data up with a table of state population's we could see just how much of an outlier it really is. In future sections we'll present tools for doing just that, however, this specific question is left as an experiment for the reader.

Saving your work
================

The complete ranking might be a useful thing to have around. Rather than computing it every time, let's use output redirection to save a copy of it::

    $ in2csv 2009.csv | csvcut -c 9,1 --skipheader | sort -n -r > 2009_ranking.csv

Note that this file won't work well with the csvkit utilities as it no longer has a header, however, you can still use ``grep`` and other Unix utilities to search through it.

Onward to merging
=================

At this point you should be comfortable with the analytical capabilities of csvkit.

Next up: :doc:`adding_another_year`.
