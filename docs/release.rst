===============
Release process
===============

#. Verify no `high priority issues <https://github.com/wireservice/csvkit/issues?q=is%3Aopen+is%3Aissue+label%3A%22High+Priority%22>`_ are outstanding.
#. Run the full test suite with fresh environments for all versions: ``tox -r`` (Everything MUST pass.)
#. Ensure these files all have the correct version number:
    * CHANGELOG
    * setup.py
    * docs/conf.py
#. Tag the release: ``git tag -a x.y.z; git push --tags``
#. Roll out to PyPI: ``python setup.py sdist upload``
#. Iterate the version number in all files where it is specified. (see list above)
#. Flag the new version for building on `Read the Docs <https://readthedocs.org/dashboard/csvkit/versions/>`_. 
#. Wait for the documentation build to finish.
#. Flag the new release as the default documentation version.
#. Announce the release on Twitter, etc. 

