#!/usr/bin/env python
__author__ = 'gicmo'

try:
    from setuptools import setup, Extension
except:
    from distutils.core import setup, Extension

import commands
import numpy as np
import sys
import os

with open("README.md") as f:
    description_text = f.read()

with open("LICENSE") as f:
    license_text = f.read()

nix_inc_dir = os.getenv('NIX_INCDIR', '/usr/local/include')
nix_lib_dir = os.getenv('NIX_LIBDIR', '/usr/local/lib')
nix_lnk_arg = '-lnix'

nixpy_sources = [
    'src/core.cc',
    'src/docstrings.cpp',
    'src/PyBlock.cpp',
    'src/PyFile.cpp',
    'src/PySection.cpp',
    'src/PyProperty.cpp',
    'src/PyValue.cpp',
    'src/PySource.cpp',
    'src/PyDataArray.cpp',
    'src/PyDimensions.cpp',
    'src/PyFeature.cpp',
    'src/PySimpleTag.cpp',
    'src/PyDataTag.cpp',
]

boost_inc_dir = os.getenv('BOOST_INCDIR', '/usr/local/include')
boost_lib_dir = os.getenv('BOOST_LIBDIR', '/usr/local/lib')
boost_lnk_arg = '-lboost_python'

native_ext = Extension('nix.core',
                       extra_compile_args = ['-std=c++11'],
                       extra_link_args=[boost_lnk_arg, nix_lnk_arg],
                       sources = nixpy_sources,
                       library_dirs = [nix_lib_dir, boost_lib_dir],
                       include_dirs = [nix_inc_dir, boost_inc_dir, np.get_include(), 'src'],
                       runtime_library_dirs = [nix_lib_dir, boost_lib_dir])

setup(name             = 'nix',
      version          = 0.1,
      author           = 'Christian Kellner',
      author_email     = 'kellner@bio.lmu.de',
      ext_modules      = [native_ext],
      packages         = ['nix', 'nix.util'],
      scripts          = [],
      tests_require    = ['nose'],
      test_suite       = 'nose.collector',
      setup_requires   = ['numpy', 'sphinx'],
      package_data     = {"nix": [license_text, description_text]},
      include_package_data = True,
      zip_safe         = False,
)
