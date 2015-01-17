===============
Getting started
===============

About this tutorial
===================

There is no better way to learn how to use a new tool than to see it applied in a real world situation. This tutorial will explain the workings of most of the csvkit utilities (including some nifty tricks) in the context of analyzing a real dataset.

The data will be using is a subset of the United States Defense Logistic Agency Law Enforcement Support Office's (LESO) 1033 Program dataset, which describes how surplus military arms have been distributed to local police forces. This data was widely cited in the aftermath of the Ferguson, Missouri protests. The particular data we are using comes from an `NPR report <http://www.npr.org/2014/09/02/342494225/mraps-and-bayonets-what-we-know-about-the-pentagons-1033-program>`_ analyzing the data.

This tutorial assumes you are comfortable in the command line, but does not assume any prior experience doing data processing or analysis.

Installing csvkit
=================

Installing csvkit is easy::

    $ sudo pip install csvkit

If you have problems installing, check out the common issues described in the :doc:`../install` section of the full documentation.

.. note::

    If you're familiar with `virtualenv <http://virtualenv.readthedocs.org/en/latest/>`_, it's better to install csvkit inside an env, in which case you should leave off the ``sudo`` in the previous command.

Getting the data
================

Let's start by creating a clean workspace::

    $ mkdir csvkit_tutorial 
    $ cd csvkit_tutorial

Now let's fetch the data::

    $ curl -L -O https://github.com/onyxfish/csvkit/raw/master/examples/realdata/ne_1033_data.xlsx

in2csv: the Excel killer
========================

For purposes of this tutorial, I've converted this data to Excel format. (NPR published it in CSV format.) If you have Excel you can open the file and take a look at it, but really, who wants to wait for Excel to load? Instead, let's make it a CSV::

    $ in2csv ne_1033_data.xlsx

You should see a CSV version of the data dumped into your terminal. All csvkit utilities write to the terminal output ("standard out") by default. This isn't very useful, so let's write it to a file instead::

    $ in2csv ne_1033_data.xlsx > data.csv

``data.csv`` will now contain a CSV version of our original file. If you aren't familiar with the ``>`` syntax, it literally means "redirect standard out to a file", but it may be more convenient to think of it as "save".

:doc:`/scripts/in2csv` will convert a variety of common file formats, including xls, xlsx and fixed-width into CSV format.

csvlook: data periscope
=======================

Now that we have some data, we probably want to get some idea of what's in it. We could open it in Excel or Google Docs, but wouldn't it be nice if we could just take a look in the command line? Enter csvlook::

    $ csvlook data.csv

Now at first the output of :doc:`/scripts/csvlook` isn't going to appear very promising. You'll see a mess of data, pipe character and dashes. That's because this dataset has many columns and they won't all fit in the terminal at once. To fix this we need to learn how to reduce our dataset before we look at it.

csvcut: data scalpel
====================

:doc:`/scripts/csvcut` is the original csvkit tool, the one that started the whole thing. With it, we can slice, delete and reorder the columns in our CSV. First, let's just see what columns are in our data::

    $ csvcut -n data.csv
      1: state
      2: county
      3: fips
      4: nsn
      5: item_name
      6: quantity
      7: ui
      8: acquisition_cost
      9: total_cost
     10: ship_date
     11: federal_supply_category
     12: federal_supply_category_name
     13: federal_supply_class
     14: federal_supply_class_name

As you'll can see, our dataset has fourteen columns. Let's take a look at just columns ``2``, ``5`` and ``6``::

    $ csvcut -c 2,5,6 data.csv

Now we've reduced our output CSV to only three columns.

We can also refer to columns by their names to make our lives easier::

    $ csvcut -c county,item_name,quantity data.csv

Putting it together with pipes
==============================

Now that we understand ``in2csv``, ``csvlook`` and ``csvcut`` we can demonstrate the power of csvkit's when combined with the standard command line "pipe". Try this command::

    $ csvcut -c county,item_name,quantity data.csv | csvlook | head

All csvkit utilities accept an input file as "standard in", in addition to as a filename. This means that we can make the output of one csvkit utility become the input of the next. In this case, the output of ``csvcut`` becomes the input to ``csvlook``. This also means we can use this output with standard unix commands such as ``head``, which prints only the first ten lines of it's input. Here, the output of ``csvlook`` becomes the input of ``head``.

Pipeability is a core feature of csvkit. Of course, you can always write your output to a file using ``>``, but many times it makes more sense to use pipes for speed and brevity.

Of course, we can also pipe ``in2csv``, combining all our previous operations into one::

    $ in2csv ne_1033_data.xlsx | csvcut -c county,item_name,quantity | csvlook | head

Summing up
==========

All the csvkit utilities work standard input and output. Any utility can be piped into another and into another and then at some point down the road redirected to a file. In this way they form a data processing "pipeline" of sorts, allowing you to do non-trivial, repeatable work without creating dozens of intermediary files.

Make sense? If you think you've got it figured out, you can move on to :doc:`2_examining_the_data`.
