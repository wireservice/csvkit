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

    Need more speed? If you're running Python 2.6 or 2.7 or you can :code:`pip install cdecimal` for a significant speed boost. This isn't installed automatically because it can create additional complications.

Developers
==========

If you are a developer that also wants to hack on csvkit, install it this way::

    git clone git://github.com/onyxfish/csvkit.git
    cd csvkit
    mkvirtualenv csvkit

    # If running Python 2
    pip install -r requirements-py2.txt

    # If running Python 3
    pip install -r requirements-py3.txt

    python setup.py develop
    tox

Before writing any code be sure to read the documentation for :doc:`contributing`.

Supported platforms
-------------------

csvkit supports the following versions of Python:

* Python 2.6+
* Python 3.3+
* `PyPy <http://pypy.org/>`_

It is tested on OSX, but has been used successfully by others on both Linux and Windows.
