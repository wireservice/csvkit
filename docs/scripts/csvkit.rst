======
csvkit
======

Description
===========

Display the installed csvkit version and available command-line tools:

.. code-block:: none

   usage: csvkit [-h] [-V]

   options:
     -h, --help     show this help message and exit
     -V, --version  show program's version number and exit

With no arguments, :code:`csvkit` displays the same overview as :code:`--help`.
The version and tool names come from the installed csvkit package. The overview
lists tools alphabetically and includes an example of getting help for a tool.

Examples
========

List the available tools:

.. code-block:: bash

   csvkit

Print only the installed version:

.. code-block:: bash

   csvkit --version

Run tools directly, for example:

.. code-block:: bash

   csvcut --help

The overview command does not accept CSV input or dispatch subcommands.
