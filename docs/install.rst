============
Installation
============

Users
=====

If you only want to use agate, install it this way::

    pip install agate

.. note::

    If you are installing on Ubuntu you may need to install the Python development headers prior to install csvkit::

        sudo apt-get install python-dev python-pip python-setuptools build-essential

.. note::

    If the installation appears to be successful but running the tools fails, try updating your version of Python setuptools::

        pip install --upgrade setuptools
        pip install --upgrade csvkit

.. note::

    If you are using Python2 and have a recent version of pip, you may need to run pip with the additional arguments :code:`--allow-external argparse`.

.. note::

    Need more speed? If you're running Python 2.7 you can :code:`pip install cdecimal` for a significant speed boost. This isn't installed automatically because it can create additional complications.

Supported platforms
===================

csvkit supports the following versions of Python:

* Python 2.7+
* Python 3.3+
* `PyPy <http://pypy.org/>`_

It is tested on OS X, but has been used successfully by others on both Linux and Windows.
