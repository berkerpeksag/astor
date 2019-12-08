# coding: utf-8

import os.path
import sys
import time

sys.path.append(os.path.pardir)

import setuputils

extensions = []

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'astor'
copyright = u'2013-%s, Berker Peksag' % time.strftime('%Y')

version = release = setuputils.read('astor/VERSION')

exclude_patterns = ['_build']

pygments_style = 'sphinx'

try:
    import sphinx_rtd_theme
except ImportError:
    html_theme = 'default'
else:
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

htmlhelp_basename = 'astordoc'
