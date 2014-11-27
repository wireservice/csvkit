======================
Contributing to csvkit
======================

Principles
==========

csvkit is to tabular data what the standard Unix text processing suite (grep, sed, cut, sort) is to text. As such, csvkit adheres to `the Unix philosophy <http://en.wikipedia.org/wiki/Unix_philosophy>`_.

#. Small is beautiful.
#. Make each program do one thing well.
#. Build a prototype as soon as possible.
#. Choose portability over efficiency.
#. Store data in flat text files.
#. Use software leverage to your advantage.
#. Use shell scripts to increase leverage and portability.
#. Avoid captive user interfaces.
#. Make every program a filter.

As there is no formally defined CSV format, csvkit encourages well-known formatting standards:

* Output favors compatability with the widest range of applications. This means that quoting is done with double-quotes and only when necessary, columns are separated with commas, and lines are terminated with unix style line endings ("\\n").

* Data that is modified or generated will prefer consistency over brevity. Floats always include at least one decimal place, even if they are round. Dates and times are written in ISO8601 format.

Process for contributing code
=============================

Contributors should use the following roadmap to guide them through the process of submitting a contribution:

#. Fork the project on `Github <https://github.com/onyxfish/csvkit>`_.
#. Check out the `issue tracker <https://github.com/onyxfish/csvkit/issues>`_ and find a task that needs to be done and is of a scope you can realistically expect to complete in a few days. Don't worry about the priority of the issues at first, but try to choose something you'll enjoy. You're much more likely to finish something to the point it can be merged if it's something you really enjoy hacking on.
#. Comment on the ticket letting everyone know you're going to be hacking on it so that nobody duplicates your effort. It's also good practice to provide some general idea of how you plan on resolving the issue so that other developers can make suggestions.
#. Write tests for the feature you're building. Follow the format of the existing tests in the test directory to see how this works. You can run all the tests with the command ``tox``.
#. Write the code. Try to stay consistent with the style and organization of the existing codebase. A good patch won't be refused for stylistic reasons, but large parts of it may be rewritten and nobody wants that. 
#. As you're coding, periodically merge in work from the master branch and verify you haven't broken anything by running the test suite.
#. Write documentation for user-facing features.
#. Once it works, is tested, and has documentation, submit a pull request on Github.
#. Wait for it to either be merged or to recieve a comment about what needs to be fixed.
#. Rejoice.

Legalese
========

To the extent that they care, contributors should keep the following legal mumbo-jumbo in mind:

The source of csvkit and therefore of any contributions are licensed under the permissive `MIT license <http://www.opensource.org/licenses/mit-license.php>`_. By submitting a patch or pull request you are agreeing to release your code under this license. You will be acknowledged in the AUTHORS file. As the owner of your specific contributions you retain the right to privately relicense your specific code contributions (and no others), however, the released version of the code can never be retracted or relicensed.

