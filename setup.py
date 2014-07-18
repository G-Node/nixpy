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
import re

with open('README.md') as f:
    description_text = f.read()

with open('LICENSE') as f:
    license_text = f.read()

with open('nix/info.py') as f:
    info = f.read()

VERSION         = re.search(r"VERSION\s*=\s*'([^']*)'", info).group(1)
AUTHOR          = re.search(r"AUTHOR\s*=\s*'([^']*)'", info).group(1)
CONTACT         = re.search(r"CONTACT\s*=\s*'([^']*)'", info).group(1)
BRIEF           = re.search(r"BRIEF\s*=\s*'([^']*)'", info).group(1)
HOMEPAGE        = re.search(r"HOMEPAGE\s*=\s*'([^']*)'", info).group(1)

def pkg_config(*packages, **kw):
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}
    for token in commands.getoutput("pkg-config --libs --cflags %s" % ' '.join(packages)).split():
        kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])

    # remove duplicated
    for k, v in kw.iteritems():
        del kw[k]
        kw[k] = list(set(v))

    return kw

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

classifiers   = [
                    'Development Status :: 3 - Alpha',
                    'Programming Language :: Python',
                    'Programming Language :: Python :: 2.6',
                    'Programming Language :: Python :: 2.7',
                    'Topic :: Scientific/Engineering'
]

native_ext    = Extension(
                    'nix.core',
                    extra_compile_args = ['-std=c++11'],
                    extra_link_args=[boost_lnk_arg, nix_lnk_arg],
                    sources = nixpy_sources,
                    runtime_library_dirs = [nix_lib_dir, boost_lib_dir],
                    **pkg_config(
                        "nix",
                        library_dirs=[boost_lib_dir],
                        include_dirs=[boost_inc_dir, np.get_include(), 'src']
                    )
                )

setup(name             = 'nix',
      version          = VERSION,
      author           = AUTHOR,
      author_email     = CONTACT,
      url              = HOMEPAGE,
      description      = BRIEF,
      long_description = description_text,
      classifiers      = classifiers,
      license          = 'BSD',
      ext_modules      = [native_ext],
      packages         = ['nix', 'nix.util'],
      scripts          = [],
      tests_require    = ['nose'],
      test_suite       = 'nose.collector',
      setup_requires   = ['numpy', 'sphinx', 'alabaster'],
      package_data     = {'nix': [license_text, description_text]},
      include_package_data = True,
      zip_safe         = False,
)
