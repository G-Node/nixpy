#!/usr/bin/env python

from __future__ import absolute_import, division, print_function

__author__ = 'gicmo'

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

# python version dependent import of getstatusoutput
try:
    from commands import getstatusoutput
except ImportError:
    from subprocess import getstatusoutput

import numpy as np
import sys
import os
import re
import distutils
import platform

from findboost import BoostPyLib

with open('README.md') as f:
    description_text = f.read()

with open('LICENSE') as f:
    license_text = f.read()

with open('nixio/info.py') as f:
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

is_win = os.name == 'nt'

nix_inc_dir = os.getenv('NIX_INCDIR', '/usr/local/include')
nix_lib_dir = os.getenv('NIX_LIBDIR', '/usr/local/lib')
if not is_win:
    nix_lnk_arg = ['-lnix']
else:
    nix_lnk_arg = ['/LIBPATH:'+nix_lib_dir, '/DEFAULTLIB:nix.lib']

nixpy_sources = [
    'src/core.cc',
    'src/docstrings.cpp',
    'src/PyExceptions.cpp',
    'src/PyBlock.cpp',
    'src/PyFile.cpp',
    'src/PySection.cpp',
    'src/PyProperty.cpp',
    'src/PySource.cpp',
    'src/PyDataArray.cpp',
    'src/PyDataSet.cpp',
    'src/PyDimensions.cpp',
    'src/PyFeature.cpp',
    'src/PyTag.cpp',
    'src/PyMultiTag.cpp',
    'src/PyResult.cpp',
    'src/PyGroup.cpp'
]

boost_inc_dir = os.getenv('BOOST_INCDIR', '/usr/local/include')
boost_lib_dir = os.getenv('BOOST_LIBDIR', '/usr/local/lib')

lib_dirs = BoostPyLib.library_search_dirs([boost_lib_dir])
boost_libs = BoostPyLib.list_in_dirs(lib_dirs)
boost_lib = BoostPyLib.find_lib_for_current_python(boost_libs)

if boost_lib is None:
    print("Could not find boost python version for %s.%s" % sys.version_info[0:2])
    print("Available boost python libs:\n" + "\n".join(map(str, boost_libs)))
    sys.exit(-1)

boost_lnk_arg = boost_lib.link_directive

classifiers   = [
                    'Development Status :: 5 - Production/Stable',
                    'Programming Language :: Python',
                    'Programming Language :: Python :: 2.6',
                    'Programming Language :: Python :: 2.7',
                    'Programming Language :: Python :: 3.4',
                    'Topic :: Scientific/Engineering'
]

native_ext    = Extension(
                    'nixio.core',
                    extra_compile_args = ['-std=c++11'] if not is_win else ['/DBOOST_PYTHON_STATIC_LIB', '/EHsc'],
                    extra_link_args=boost_lnk_arg + nix_lnk_arg,
                    sources = nixpy_sources,
                    runtime_library_dirs = [nix_lib_dir, boost_lib_dir] if not is_win else None,
                    **pkg_config(
                        "nixio",
                        library_dirs=[boost_lib_dir, nix_lib_dir],
                        include_dirs=[boost_inc_dir, nix_inc_dir, np.get_include(), 'src'],
                        ignore_error=True
                    )
                )

setup(name             = 'nixio',
      version          = VERSION,
      author           = AUTHOR,
      author_email     = CONTACT,
      url              = HOMEPAGE,
      description      = BRIEF,
      long_description = description_text,
      classifiers      = classifiers,
      license          = 'BSD',
      ext_modules      = [native_ext],
      packages         = ['nixio', 'nixio.util'],
      scripts          = [],
      tests_require    = ['nose'],
      test_suite       = 'nose.collector',
      setup_requires   = ['h5py', 'numpy'],
      package_data     = {'nixio': [license_text, description_text]},
      include_package_data = True,
      zip_safe         = False,
)
