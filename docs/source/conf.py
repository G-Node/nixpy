# Copyright © 2014-2021, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from nixio.info import RELEASE, COPYRIGHT, BRIEF

# general config
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx', 'sphinx.ext.autosectionlabel']
source_suffix = '.rst'
master_doc = 'index'
project = BRIEF
copyright = COPYRIGHT
release = RELEASE
exclude_patterns = []
pygments_style = 'sphinx'

# html options
htmlhelp_basename = 'nixio'
try:
    html_theme = 'sphinx_rtd_theme'
    html_sidebars = {'**': ['about.html', 'navigation.html', 'searchbox.html']}

    html_theme_options = {'logo_only': True,
                          'display_version': True,
                          'style_external_links': True,
                          'prev_next_buttons_location': "both"}

    html_logo = "nix_logo.png"

except ImportError:
    html_theme = 'default'

# intersphinx configuration
intersphinx_mapping = {'http://docs.python.org/': None,
                       'http://docs.scipy.org/doc/numpy': None}
