# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'csvkit'
copyright = '2016, Christopher Groskopf and James McKinney'
version = '2.0.1'
release = version

# -- General configuration -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'

htmlhelp_basename = 'csvkitdoc'

autodoc_default_options = {
    'members': None,
    'member-order': 'bysource',
    'show-inheritance': True,
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

man_pages = []
for filename in os.listdir('scripts'):
    name = os.path.splitext(filename)[0]
    man_pages.append((
        os.path.join('scripts', name),
        name,
        f'{name} Documentation',
        ['Christopher Groskopf and contributors'],
        1,
    ))
