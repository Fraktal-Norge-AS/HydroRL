# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))


# -- Project information -----------------------------------------------------

project = 'HydroRL'
copyright = '2022, Fraktal Norge AS'
author = 'Fraktal Norge AS'

# The full version, including alpha/beta/rc tags
release = '0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',    
    'sphinxcontrib.openapi',
    'myst_nb',
    'sphinxcontrib.bibtex'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    "collapse_navigation" : False
}
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, maps document names to template names.
#
# html_sidebars = { '**': ['globaltoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html'], }


# -- MyST Extensions  --------------------------------------------------------
myst_enable_extensions = [
    "dollarmath",
    "html_image",
    "colon_fence",
    "amsmath"
]

## Fix bug in sphinx_rtd_theme that math eq. no. is not aligned right.
html_static_path = ['css']
html_css_files = ['custom.css']


# -- MyST Notebook Extensions ------------------------------------------------

# auto: Will only execute notebooks that are missing at least one output. (Default)
# force: Executes all notebooks
# cache: Cache execution with jupyter-cache. See: https://myst-nb.readthedocs.io/en/latest/use/execute.html#execute-cache
# off: Turn of notebook execution
jupyter_execute_notebooks = "off"
execution_excludepatterns = []
html_js_files = [    
    "https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js"    
    ]


# -- Bibtex Extensions ------------------------------------------------
bibtex_bibfiles = ['bibliography/refs.bib']
bibtex_default_style = 'unsrt'