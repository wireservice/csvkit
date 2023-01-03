===============
Release process
===============

.. admonition:: One-time setup

   .. code-block:: bash

      pip install --upgrade build twine

#. All tests pass on continuous integration
#. The changelog is up-to-date and dated
#. The version number is correct in:

    -  setup.py
    -  docs/conf.py
    -  csvkit/cli.py

#. Check for new authors:

   .. code-block:: bash

      git log --perl-regexp --author='^((?!James McKinney).*)$'

#. Tag the release:

   .. code-block:: bash

      git tag -a x.y.z -m 'x.y.z release.'
      git push --follow-tags

#. Upload to PyPI:

   .. code-block:: bash

      rm -rf dist
      python -m build --sdist --wheel
      twine upload dist/*

#. Build the documentation on ReadTheDocs manually
