===============
Getting started
===============

Description
===========

There is no better way to learn how to use a new tool than to see it applied in a real world situation. This tutorial will explain the workings of most of the csvkit utilities (including some nifty tricks) in the context of analyzing a real dataset from `data.gov <http://data.gov>`_.

The dataset that I've chosen to work with is recipients of United States Department of Veteran Affairs education benefits, by state and year. For those who are unfamiliar, these are individuals whom the US government is paying to attend school as a benefit of their having served in the military (or, in some case, having had a close relative who served). We will be working with `2009 <http://www.data.gov/raw/4029>`_ and `2010 <http://www.data.gov/raw/4509>`_ data.

If you have never done much data processing work this tutorial should double as a reasonable introduction to that as well.

Following along
===============

I strongly encourage anyone reading this tutorial to work through the examples, however, if you really just want to see how of the tools are applied then you can read through `the complete bash script for the entire tutorial <https://gist.github.com/924589>`_.

Getting the data
================

Let's start by creating a clean workspace::

    $ mkdir va_benefits
    $ cd va_benefits

Now let's fetch the 2009 data file and rename it:

    $ wget -O 2009.csv http://www.data.gov/download/4029/csv

.. note:: 

	Don't have wget? `brew install wget`


At first glance this may appear to have worked. You will end up with a ``2009.csv`` file in your working directory. However, when I said this tutorial would tackle real-world problems, I meant it. Let's take a look at the contents of that file::

    $ cat 2009.csv
    <html><head><title>Request Rejected</title></head><body>The requested URL was rejected. <br><br>Please contact the VA Network and Security Operations Center at 1-800-877-4328 or email VANSOC@va.gov, if you feel this is in error. <br><br>Your support ID is: 1193122742127908960<br> Appliance name: gwwrpx1<br></body></html>

It seems `data.gov <http://data.gov>`_ is redirecting our request to the VA's website and they don't like people fetching down files from the command-line. Fortunantely for us, this is a terribly naive thing to do, and easy to work around.

Let's pretend our request is coming from Google Chrome instead of wget::

    $ wget -O 2009.csv -U "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.205 Safari/534.16" http://www.data.gov/download/4029/csv

And use the Unix text-processing utility ``head`` to check the first five lines and make sure the file looks right this time::

    $ head -n 5 2009.csv 
    State Name,State Abbreviate,Code,Montgomery GI Bill-Active Duty,Montgomery GI Bill- Selective Reserve,Dependents' Educational Assistance,Reserve Educational Assistance Program,Post-Vietnam Era Veteran's Educational Assistance Program,TOTAL,
    ALABAMA,AL,01,"6,718","1,728","2,703","1,269",8,"12,426",
    ALASKA,AK,02,776,154,166,60,2,"1,158",
    ARIZONA,AZ,04,"26,822","2,005","3,137","2,011",11,"33,986",
    ARKANSAS,AR,05,"2,061",988,"1,575",886,3,"5,513",

That looks better so let's fetch the 2010 data using the same trick::

    $ wget -O 2010.csv -U "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.205 Safari/534.16" http://www.data.gov/download/4509/csv

If you're working from a copy of the csvkit source code, you can also find these files in the ``examples/realdata`` folder with their default names, ``FY09_EDU_Recipients_by_State.csv`` and ``Datagov_FY10_EDU_recp_by_State.csv``, but getting them this way was a lot more fun, right?

Fixing the files with sed
=========================

Nothing is ever easy when you're working with government data. We've got one more problem before we can get down to brass tacks and start hacking these files. The first file looked fine, but let's check out the ``head`` of that second file::

    $ head -n 5 2010.csv 
    ,,,,,,,,
    Number of Beneficaries (Students) Who Recieved VA Education Benefit By State During FY 2010,,,,,,,,
    State Name,State Abbreviate,Post-9/11GI Bill Program,Montgomery GI Bill - Active Duty,Montgomery GI Bill - Selective Reserve,Dependents' Educational Assistance,Reserve Educational Assistance Program,Post-Vietnam Era Veteran's Educational Assistance Program,TOTAL
    ALABAMA,AL,7738,5779,2075,3102,883,5,"19,582"
    ALASKA,AK,1781,561,170,164,28,1,"2,705"

As you can see, this multiple header lines.  We need to modify this file to fix the issue, but as a matter of best practice let's backup our originals first::

    $ cp 2009.csv 2009_original.csv
    $ cp 2010.csv 2010_original.csv

With that done let's use the old hacker standby ``sed`` to kill those first two header lines::

    $ cat 2010_original.csv | sed "1,2d" > 2010.csv

``sed`` is an abbreviation for "stream editor", which is a useful phrase to keep in mind if you're not used to working with these tools. csvkit and the other tools introduced in the next chapter all operate on streams of data, processing them one line at a time. The ``sed`` command we just used translates to, "Select lines 1 and 2 of the input, (d)elete them."

The previous command also introduces a couple other concepts that are much more important than the indiosyncrancies of ``sed``.

Piping
======

The first is piping. If you haven't spent too much time in the terminal you may be unfamiliar with the ``|`` (pipe). The pipe means, "take the output of the former command and use it as input to the latter." So in this case the output of ``cat`` (which simply prints a file) is being piped into ``sed``.

Output redirection
==================

The second interesting thing is output redirection. The ``>`` character means, send output from this command to a file. If I had used ``>>`` it would have been appended to the end of the file rather than overwriting it. This is important because by default ``sed`` will simply send its output to the console, which is great for piping, but not very useful if you want to save your results.

Putting it together
===================

All the csvkit utilities work with the concepts of piping and output redirection. The output of any utility can be piped into another and into another and then at some point down the road redirected to a file. In this way they form a data processing "pipeline" of sorts, allowing you to do non-trivial, repeatable work without creating dozens of intermediary files.

Make sense? If you think you've got it figured out, you can move on to :doc:`examining_the_data`.
