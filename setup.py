#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)#, unicode_literals)

__author__ = 'gicmo'

try:
    from setuptools import setup, Extension
except:
    from distutils.core import setup, Extension

# python version dependent import of getstatusoutput
try:
	from commands import getstatusoutput
except:
	from subprocess import getstatusoutput

import numpy as np
import sys
import os
import re
import fnmatch
import distutils

def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

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

# Replaced StandardError with Exception since StandardError is removed in Py3.x
class PackageNotFoundError(Exception):
    pass

def pkg_config(*packages, **kw):
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}

    ignore_error = 'ignore_error' in kw
    if ignore_error:
        del kw['ignore_error']

    pkg_string = ' '.join(packages)
    status, out = getstatusoutput("pkg-config --libs --cflags " + pkg_string)
    if status != 0:
        err_str = 'Some packages were not found: %s [%s]' % (pkg_string, out)
        if ignore_error:
            sys.stderr.write('WARNING: ' + err_str)
            out = ''
        else:
            raise PackageNotFoundError(err_str)

    for token in out.split():
        kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])

    # remove duplicated
    # replaced .iteritems() with .items, since .iteritems() is not available in Py3.x
    # could lead to increased memory usage and computation time.
    for k, v in kw.items():
        del kw[k]
        kw[k] = list(set(v))

    return kw

nix_inc_dir = os.getenv('NIX_INCDIR', '/usr/local/include')
nix_lib_dir = os.getenv('NIX_LIBDIR', '/usr/local/lib')
if os.name != 'nt':
    nix_lnk_arg = ['-lnix']
else:
    nix_lnk_arg = ['/LIBPATH:'+nix_lib_dir, '/DEFAULTLIB:nix.lib']

nixpy_sources = [
    'src/PyUtil.cpp',
    'src/core.cc',
    'src/docstrings.cpp',
    'src/PyExceptions.cpp',
    'src/PyBlock.cpp',
    'src/PyFile.cpp',
    'src/PySection.cpp',
    'src/PyProperty.cpp',
    'src/PyValue.cpp',
    'src/PySource.cpp',
    'src/PyDataArray.cpp',
    'src/PyDataSet.cpp',
    'src/PyDimensions.cpp',
    'src/PyFeature.cpp',
    'src/PyTag.cpp',
    'src/PyMultiTag.cpp',
    'src/PyResult.cpp'
]

boost_inc_dir = os.getenv('BOOST_INCDIR', '/usr/local/include')
boost_lib_dir = os.getenv('BOOST_LIBDIR', '/usr/local/lib')
if os.name != 'nt':
    boost_lnk_arg = ['-lboost_python']
else:
    boostlib = find('libboost_python*.lib', boost_lib_dir)
    boost_lnk_arg = ['/LIBPATH:'+boost_lib_dir, '/DEFAULTLIB:'+boostlib[0]]

classifiers   = [
                    'Development Status :: 4 - Beta',
                    'Programming Language :: Python',
                    'Programming Language :: Python :: 2.6',
                    'Programming Language :: Python :: 2.7',
                    'Topic :: Scientific/Engineering'
]

native_ext    = Extension(
                    'nix.core',
                    extra_compile_args = ['-std=c++11'] if os.name!='nt' else ['/DBOOST_PYTHON_STATIC_LIB', '/EHsc'],
                    extra_link_args=boost_lnk_arg + nix_lnk_arg,
                    sources = nixpy_sources,
                    runtime_library_dirs = [nix_lib_dir, boost_lib_dir] if os.name!='nt' else None,
                    **pkg_config(
                        "nix",
                        library_dirs=[boost_lib_dir, nix_lib_dir],
                        include_dirs=[boost_inc_dir, nix_inc_dir, np.get_include(), 'src'],
                        ignore_error=True
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
      setup_requires   = ['numpy', 'sphinx'],
      package_data     = {'nix': [license_text, description_text]},
      include_package_data = True,
      zip_safe         = False,
)
