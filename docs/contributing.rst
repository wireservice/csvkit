======================
Contributing to csvkit
======================

Getting Started
===============

Set up your environment for development::

    git clone git://github.com/wireservice/csvkit.git
    cd csvkit
    mkvirtualenv csvkit

    # If running Python 2:
    pip install -r requirements-py2.txt

    # If running Python 3:
    pip install -r requirements-py3.txt

    python setup.py develop
    tox

New Tools
=========

The maintainers have decided not to merge or maintain new tools; there is simply not enough time to do so. Our focus is instead on making the existing tools as good as possible. We welcome patches to improve existing tools.

We encourage you to create and maintain your own tools as separate Python packages. You may want to use the `agate <http://agate.readthedocs.io/>`_ library, which csvkit uses for most of its CSV reading and writing. Doing so will make it easier to maintain common behavior with csvkit’s tools.

Principles
==========

csvkit is to tables as Unix text processing commands (cut, grep, cat, sort) are to text. As such, csvkit adheres to `the Unix philosophy <http://en.wikipedia.org/wiki/Unix_philosophy>`_.

#. Small is beautiful.
#. Make each program do one thing well.
#. Build a prototype as soon as possible.
#. Choose portability over efficiency.
#. Store data in flat text files.
#. Use software leverage to your advantage.
#. Use shell scripts to increase leverage and portability.
#. Avoid captive user interfaces.
#. Make every program a filter.

As there is no single, standard CSV format, csvkit encourages popular formatting options:

* Output targets broad compatibility. Quoting is done with double-quotes and only when required, fields are delimited with commas, and rows are terminated with Unix line endings ("\\n").

* Output favors consistency over brevity. Floats always include at least one decimal place, even if they are round. Dates and times are output in ISO 8601 format.

How to contribute
=================

#. Fork the project on `GitHub <https://github.com/wireservice/csvkit>`_.
#. Look through the `open issues <https://github.com/wireservice/csvkit/issues>`_ for a task that you can realistically expect to complete in a few days. Don't worry about the issue's priority; instead, choose something you'll enjoy. You're more likely to finish something if you enjoy hacking on it.
#. Comment on the issue to let people know you're going to work on it so that no one duplicates your effort. It's good practice to provide a general idea of how you plan to resolve the issue so that others can make suggestions.
#. Write tests for any changes to the code's behavior. Follow the format of the tests in the ``tests/`` directory to see how this works. You can run all the tests with the command ``tox``, or just your Python version's with ``nosetests`` (faster).
#. Write the code. Try to be consistent with the style and organization of the existing code. A good contribution won't be refused for stylistic reasons, but large parts of it may be rewritten and nobody wants that.
#. As you're working, periodically merge in changes from the upstream master branch to avoid having to resolve large merge conflicts. Check that you haven't broken anything by running the tests.
#. Write documentation for any user-facing features.
#. Once it works, is tested, and is documented, submit a pull request on GitHub.
#. Wait for it to be merged or for a comment about what needs to be changed.
#. Rejoice.

Streaming and buffering
=======================

Some tools must read an entire file before writing any output; the tool "buffers" the file into memory. For example, ''csvsort'' cannot write any output before reading the entire file, because it's always possible that the next record it reads must go at the start of the sorted list.

Other tools, that operate on individual records, can write a record immediately after reading and transforming it. Records are "streamed" through the tool. Streaming tools produce output faster and require less memory than buffering tools.

Although all the tools that stream could buffer instead, we try to maintain the streaming behavior for performance reasons. The following tools stream:

* ''csvclean''
* ''csvcut''
* ''csvformat''
* ''csvgrep''
* ''csvjson'' if both the ''--stream'' and ''--no-inference'' flags are set
* ''csvsql''
* ''csvstack''
* ''in2csv'' if ''--format'' is set to either ''csv'' or ''ndjson'' and the ''--no-inference'' flag is set
* ''sql2csv''

The following tools buffer:

* ''csvjoin''
* ''csvjson'' unless both the ''--stream'' and ''--no-inference'' flags are set
* ''csvlook''
* ''csvsort''
* ''csvstat''
* ''in2csv'' unless ''--format'' is set to either ''csv'' or ''ndjson'' and the ''--no-inference'' flag is set

Legalese
========

To the extent that contributors care, they should keep the following legal mumbo-jumbo in mind:

The source of csvkit and therefore of any contributions are licensed under the permissive `MIT license <http://www.opensource.org/licenses/mit-license.php>`_. By submitting a patch or pull request you are agreeing to release your contribution under this license. You will be acknowledged in the AUTHORS file. As the owner of your specific contributions you retain the right to privately relicense your specific contributions (and no others), however, the released version of the code can never be retracted or relicensed.

