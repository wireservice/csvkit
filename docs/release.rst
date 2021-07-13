===============
Release process
===============

#. All tests pass on continuous integration
#. The changelog is up-to-date and dated
#. The version number is correct in:
    * setup.py
    * docs/conf.py
    * csvkit/cli.py
#. Check for new authors: ``git log --invert-grep --author='James McKinney'``
#. Tag the release: ``git tag -a x.y.z -m 'x.y.z release.'; git push --follow-tags``
#. Upload to PyPI: ``rm -rf dist; python setup.py sdist bdist_wheel; twine upload dist/*``
#. Build the documentation on ReadTheDocs manually
