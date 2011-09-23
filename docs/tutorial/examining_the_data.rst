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

This tells us a few things about the dataset, including that the final column doesn't have a name. However, it doesn't tell us anything about what sort of data is in each column. Let's try peeking at a couple columns to try to figure that out::

    $ csvcut -c 2,3 2009.csv | head -n 5
    State Name,Code
    AL,01
    AK,02
    AZ,04
    AR,05

Now we see the power of ``csvcut``. Using the -c flag we are able to specify columns we want to extract from the input. We also use Unix utility ``head`` to look at just the first five rows of output. From the look of things the "Code" column is a identifier that is unique to each state. It also appears that the dataset is alphabetical by state.

Statistics on demand with csvstat
=================================

Another utility included with csvkit is :doc:`/scripts/csvstat`, which mimics the summary() function from the computational statistics programming language `"R" <http://www.r-project.org/>`_.

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

Like ``csvcut``, ``csvstat`` lists columns with their numbers (in this case the column numbers are those of the CSV file *output* by ``csvcut``). However, ``csvstat`` also performs type inference on the columns and computes relevant statistics based on their types. In this case we have a *unicode* column (internally csvkit uses unicode exclusively to represent text), and two *int* (integer) columns. For the unicode column we know it contains nulls (blanks), that it has 53 unique values, that the longest value is 17 characters, and we also have five examples of data from that column.

From the statistics on the integer columns we can see that the median number of indviduals exercising VA benefits across the states is 6520, of which 3548 is the median number exercising the GI Bill while on active duty. 

We also see that the final column of the original CSV not only lacks a header, but is entirely empty. (Which is the same thing as saying that every row in this file included a trailing comma.)

If this dataset had included a column of dates or times, ``csvstat`` would have displayed the range and other details relevant to time-sequences. 

Searching for rows with csvgrep
===============================

After reviewing the summary statistics you might wonder where your home state falls in the order. To get a simple answer to the question we can use :doc:`/scripts/csvgrep` to search for the state's name amongst the rows. Let's also use csvcut to just look at the columns we care about::

    $ csvcut -c 1,"TOTAL" 2009.csv | csvgrep -c 1 -m ILLINOIS
    State Name,TOTAL
    ILLINOIS,"21,964"

In this case we are searching for the value "ILLINOIS" in the first column of the input. We can also build a more-powerful and less-verbose search by using the regular expressions flag::

    $ csvcut -c 1,"TOTAL" 2009.csv | csvgrep -c 1 -r "^I"
    State Name,TOTAL
    ILLINOIS,"21,964"

Here we have found all the states that start with the letter "I".

What if we wanted to know where Illinois ranks amongst the states with individuals claiming VA benefits? In order to answer that we need to learn a few more tricks.

Flipping column order with csvcut
=================================

*(Note: In the next few sections we will repeat some commands to show how you can build up a complex operation as a sequence of simple ones.)*

Returning for a moment to :doc:`/scripts/csvcut`, we can use its column selection logic as a powertool for reordering columns. Let's pare back the number of columns and make the column we are most interested in be first::

    $ csvcut -c 9,1 2009.csv | head -n 5
    TOTAL,State Name
    12426,ALABAMA
    1158,ALASKA
    33986,ARIZONA
    5513,ARKANSAS

Sorting with csvsort
====================

Now we can use :doc:`/scripts/csvsort` to sort the rows by the first column::

    $ csvcut -c 9,1 2009.csv | csvsort -r | head -n 5
    TOTAL,State Name
    46897,CALIFORNIA
    40402,TEXAS
    36394,FLORIDA
    33986,ARIZONA

The -r tells ``csvsort`` to sort in descending order.

We can now see that Illinois ranks fifth for individuals claiming VA benefits, behind mostly larger states, although Arizona is a surprising name to appear in the top five, given its relative size.

This works well for finding Illinois' rank as its in the top five, but if it had been further down the list we would have had to count rows to determine its rank. That's inefficient and there is a better way.

Using line numbers as proxy for rank
====================================

The ``-l`` flag is a special flag that can be passed to any csvkit utility in order to add a column of line numbers to its output. Since this data is being sorted we can use those line numbers as a proxy for rank::

    $ csvcut -c 9,1 2009.csv | csvsort -r -l | head -n 11 
    line_number,TOTAL,State Name
    1,46897,CALIFORNIA
    2,40402,TEXAS
    3,36394,FLORIDA
    4,33986,ARIZONA
    5,21964,ILLINOIS
    6,20541,VIRGINIA
    7,18236,GEORGIA
    8,15730,NORTH CAROLINA
    9,13967,NEW YORK
    10,13962,MISSOURI

Missouri had the tenth largest population of individuals claiming veterans education benefits.

If we were to join this data up with a table of state population's we could see how much of an outlier state's like Arizona and Missouri are. In future sections we'll present tools for doing just that, however, this specific question is left as an experiment for the reader.

Reading through data with csvlook and less
==========================================

You may notice in the previous output that starting on line ten the total numbers cease to line up correctly. This problem would be worse if we hadn't reordered the columns to put the number first.  For this reason CSV is often somewhat difficult to work with in the terminal. To mitigate this problem we can use :doc:`/scripts/csvlook` to display the data in a fixed-width table::

    $ csvcut -c 9,1 2009.csv | csvsort -r -l | csvlook
    ---------------------------------------------
    |  line_number | TOTAL | State Name         |
    ---------------------------------------------
    |  1           | 46897 | CALIFORNIA         |
    |  2           | 40402 | TEXAS              |
    |  3           | 36394 | FLORIDA            |
    |  4           | 33986 | ARIZONA            |
    |  5           | 21964 | ILLINOIS           |
    |  6           | 20541 | VIRGINIA           |
    |  7           | 18236 | GEORGIA            |
    |  8           | 15730 | NORTH CAROLINA     |
    |  9           | 13967 | NEW YORK           |
    |  10          | 13962 | MISSOURI           |
    [...]

*Hint: If your table doesn't render like this one, try making you terminal window wider.*

Isn't that better? You may still find it annoying it to have the entire contents of the table get printed to your terminal window. To better manage the output try piping it to the unix utility ``less`` or, if you're just glancing at it, ``more``.


Saving your work
================

The complete ranking might be a useful thing to have around. Rather than computing it every time, let's use output redirection to save a copy of it::

    $ csvcut -c 9,1 2009.csv | csvsort -r -l > 2009_ranking.csv

Onward to merging
=================

At this point you should be comfortable with the analytical capabilities of csvkit.

Next up: :doc:`adding_another_year`.
