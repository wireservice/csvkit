===============
Release process
===============

#. All tests pass on continuous integration
#. The changelog is up-to-date and dated
#. If new options are added, regenerate the usage information in the documentation with, for example:

   .. code-block:: bash

      stty cols 80
      csvformat -h
      stty sane

#. The version number is correct in:

   -  setup.py
   -  docs/conf.py
   -  csvkit/cli.py

#. Regenerate the man pages:

   .. code-block:: bash

      sphinx-build -b man docs man

#. Check for new authors:

   .. code-block:: bash

      git log --perl-regexp --author='^((?!James McKinney).*)$'

#. Tag the release:

   .. code-block:: bash

      git tag -a x.y.z -m 'x.y.z release.'
      git push --follow-tags
