# -*- coding: utf-8 -*-
#
# sample documentation build configuration file, created by
# sphinx-quickstart on Mon Apr 16 21:22:43 2012.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Not that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import sys
import os

import sphinx_rtd_theme


# -- Support building doc without install --------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.insert(0, os.path.abspath('.'))

# Get the project root dir, which is the parent parent dir of this
cwd = os.getcwd()
project_root = os.path.dirname(os.path.dirname(cwd))

# Insert the project root dir as the first element in the PYTHONPATH.
# This lets us ensure that the source package is imported, and that its
# version is used.
sys.path.insert(0, os.path.join(project_root, 'src'))

from pynwb._version import get_versions


# -- Autodoc configuration -----------------------------------------------------

autoclass_content = 'both'
autodoc_docstring_signature = True
autodoc_member_order = 'bysource'

# -- General configuration -----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.extlinks',
    'sphinx_gallery.gen_gallery',
    'sphinx_copybutton',
]

from sphinx_gallery.sorting import ExplicitOrder
from sphinx_gallery.sorting import ExampleTitleSortKey


class CustomSphinxGallerySectionSortKey(ExampleTitleSortKey):
    """
    Define the key to be used to sort sphinx galleries sections

    :param src_dir : The source directory.
    :type srd_dir: str
    """
    # Define a partial ordered list of galleries for all subsections. Galleries not
    # listed here will be added in alphabetical order based on title after the
    # explicitly listed galleries
    GALLERY_ORDER = {
        'general': ['file.py'],
        # Sort domain-specific tutorials based on domain to group tutorials belonging to the same domain
        'domain': ['ecephys.py',
                   'ophys.py',
                   'plot_icephys.py', 'plot_icephys_pandas.py', 'icephys.py',
                   'plot_behavior.py',
                   'brain_observatory.py'],
        'advanced_io': []
    }

    def __call__(self, filename):
        """
        Compute index to use for sorting galleries.

        Return the explicit index of the gallery if defined as part of self.GALLERY_ORDER
        and otherwise compute a score based on the title of the gallery to ensure galleries
        are sorted alphabetically by default
        """
        import string
        import math

        # Get the ordered list of gallery files for the current source dir
        explicit_order = self.GALLERY_ORDER.get(os.path.basename(self.src_dir), [])
        # If the file is in the explicit order then return its index
        if filename in explicit_order:
            sort_index = explicit_order.index(filename)
        # Else sort alphabetically based on the title by computing a corresponding
        # floating point index based on the characters of the titles
        else:
            title = super().__call__(filename)
            # map the characters of the title to a floating point number
            # based on the numerical index of the individual lowercase characters
            sort_index = len(explicit_order)  # all explicitly ordered galleries come first
            for i, v in enumerate(title.lower()):
                # get the index of the current character
                curr_index = (string.ascii_lowercase.index(v)
                              if v in string.ascii_lowercase
                              else len(string.ascii_lowercase))
                # shift the value based on its position in the title string and
                # add it to the sort_index value
                sort_index += curr_index / math.pow(10, ((i+1) * 2))
        return sort_index


sphinx_gallery_conf = {
    # path to your examples scripts
    'examples_dirs': ['../gallery'],
    # path where to save gallery generated examples
    'gallery_dirs': ['tutorials'],
    'subsection_order': ExplicitOrder(['../gallery/general', '../gallery/domain', '../gallery/advanced_io']),
    'backreferences_dir': 'gen_modules/backreferences',
    'min_reported_time': 5,
    'remove_config_comments': True,
    'within_subsection_order': CustomSphinxGallerySectionSortKey,
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3.9', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
    'h5py': ('https://docs.h5py.org/en/latest/', None),
    'hdmf': ('https://hdmf.readthedocs.io/en/latest/', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),
    'dandi': ('https://dandi.readthedocs.io/en/stable/', None),
}

extlinks = {'incf_lesson': ('https://training.incf.org/lesson/%s', ''),
            'incf_collection': ('https://training.incf.org/collection/%s', ''),
            'nwb_extension': ('https://github.com/nwb-extensions/%s', ''),
            'pynwb': ('https://github.com/NeurodataWithoutBorders/pynwb/%s', ''),
            'nwb_overview': ('https://nwb-overview.readthedocs.io/en/latest/%s', '')}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'source/index'
master_doc = 'index'

# General information about the project.
project = u'PyNWB'
copyright = u'2017-2022, Neurodata Without Borders'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '{}'.format(get_versions()['version'])
# The full version, including alpha/beta/rc tags.
release = '{}'.format(get_versions()['version'])

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
# language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
# today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'test.py']

# The reST default role (used for this markup: `text`) to use for all documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = False

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
# add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []


# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
# html_theme = 'default'
# html_theme = "sphinxdoc"
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    # "style_nav_header_background": "#AFD2E8"
    "style_nav_header_background": "#000000"
}

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    'css/custom.css',
]

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
# html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
# html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = None
html_logo = 'figures/logo_pynwb_with_margin.png'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = 'figures/favicon_96.png'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
# html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_domain_indices = True

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
# html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
# html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'sampledoc'


# -- Options for LaTeX output --------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    # 'print()reamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
# latex_documents = [
#  ('index', 'sample.tex', u'sample Documentation',
#   u'Kenneth Reitz', 'manual'),
# ]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
latex_logo = 'figures/logo_pynwb_with_margin.png'

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# If true, show page references after internal links.
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_domain_indices = True


# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
# man_pages = [
#    ('index', 'sample', u'sample Documentation',
#     [u'Kenneth Reitz'], 1)
# ]
#
# If true, show URL addresses after external links.
# man_show_urls = False
#
#
# # -- Options for Texinfo output ------------------------------------------------
#
# # Grouping the document tree into Texinfo files. List of tuples
# # (source start file, target name, title, author,
# #  dir menu entry, description, category)
# texinfo_documents = [
#  ('index', 'sample', u'sample Documentation',
#   u'Kenneth Reitz', 'sample', 'One line description of project.',
#   'Miscellaneous'),
# ]

# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'


# -- PyNWB sphinx extension ----------------------------------------------------

#
# see http://www.sphinx-doc.org/en/master/extdev/appapi.html
#

def run_apidoc(_):
    from sphinx.ext.apidoc import main as apidoc_main
    import os
    import sys
    out_dir = os.path.dirname(__file__)
    src_dir = os.path.join(out_dir, '../../src')
    sys.path.append(src_dir)
    apidoc_main(['-f', '-e', '--no-toc', '-o', out_dir, src_dir])


from abc import abstractproperty

def skip(app, what, name, obj, skip, options):
    if isinstance(obj, abstractproperty) or getattr(obj, '__isabstractmethod__', False):
        return False
    elif name == "__getitem__":
        return False
    return skip


def setup(app):
    app.connect('builder-inited', run_apidoc)
    app.add_css_file("theme_overrides.css")  # overrides for wide tables in RTD theme
    app.connect("autodoc-skip-member", skip)
