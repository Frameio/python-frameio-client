import os
import sys
sys.path.insert(0, os.path.abspath('..'))

import frameioclient

PACKAGE_TITLE = 'Frame.io Python SDK'
PACKAGE_NAME = 'frameioclient'
PACKAGE_DIR = '../frameioclient'
AUTHOR_NAME = 'Frame.io'

try:
    RELEASE = frameioclient.ClientVersion.version()
except AttributeError:
    RELEASE = 'unknown'

version = RELEASE.split('.')[0]

# -- Project information -----------------------------------------------------

project = PACKAGE_TITLE
copyright = 'MIT License 2022, Frame.io'
author = AUTHOR_NAME

# The full version, including alpha/beta/rc tags
release = RELEASE


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinxcontrib.restbuilder',
    'sphinx_jekyll_builder',
    'sphinx_autodoc_typehints'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'build/*', 'examples/*', 'tests/*', '*.cfg', '.vscode/*', '.github/*', '.circleci/*', '.pytest_cache/*', 'dist/*']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'furo'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
