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

try:
    import numpy as np
    np_inc_dir = np.get_include()
except ImportError:
    np_inc_dir = ""

import sys
import os

from nixio.info import VERSION, AUTHOR, CONTACT, BRIEF, HOMEPAGE

from scripts.findboost import BoostPyLib
from scripts.checknix import check_nix


# Replaced StandardError with Exception since StandardError is removed in Py3.x
class PackageNotFoundError(Exception):
    pass


with open('README.rst') as f:
    description_text = f.read()

with open('LICENSE') as f:
    license_text = f.read()


is_win = os.name == 'nt'

if "dev" in VERSION:
    if is_win:
        colorcodes = ("", "")
    else:
        colorcodes = ("\033[93m", "\033[0m")
    sys.stderr.write("{}WARNING: You are building a development version "
                     "of nixpy.{}\n".format(*colorcodes))


def pkg_config(*packages, **kw):
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}

    ignore_error = 'ignore_error' in kw
    if ignore_error:
        del kw['ignore_error']

    pkg_string = ' '.join(packages)
    status, out = getstatusoutput("pkg-config --libs --cflags " + pkg_string)
    if status != 0:
        err_str = 'Some packages were not found: %s\n\t%s' % (
            pkg_string, out.replace("\n", "\n\t")
        )
        if ignore_error:
            sys.stderr.write('WARNING: {}\n'.format(err_str))
            out = ''
        else:
            raise PackageNotFoundError(err_str)

    for token in out.split():
        kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])

    # remove duplicated
    # could lead to increased memory usage and computation time.
    for k, v in kw.items():
        del kw[k]
        kw[k] = list(set(v))

    return kw


def get_wheel_data():
    data = []
    bin = os.environ.get('NIXPY_WHEEL_BINARIES', '')
    if bin and os.path.isdir(bin):
        data.append(
            ('share/nixio/bin',
             [os.path.join(bin, f) for f in os.listdir(bin)]))
    return data


nix_inc_dir = os.getenv('NIX_INCDIR', '/usr/local/include')
nix_lib_dir = os.getenv('NIX_LIBDIR', '/usr/local/lib')
nix_lib = 'nix'

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

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Scientific/Engineering'
]

boost_inc_dir = os.getenv('BOOST_INCDIR', '/usr/local/include')
boost_lib_dir = os.getenv('BOOST_LIBDIR', '/usr/local/lib')
lib_dirs = BoostPyLib.library_search_dirs([boost_lib_dir])\
    if not is_win else []
boost_libs = BoostPyLib.list_in_dirs(lib_dirs)
boost_lib = BoostPyLib.find_lib_for_current_python(boost_libs)
library_dirs = [boost_lib_dir, nix_lib_dir]
include_dirs = [boost_inc_dir, nix_inc_dir, np_inc_dir, 'src']
libraries = [nix_lib]
compile_args = ['--std=c++11'] if not is_win else ['/DBOOST_PYTHON_STATIC_LIB',
                                                   '/EHsc']

if "--without-nix" in sys.argv:
    sys.argv.remove("--without-nix")
    with_nix = False
elif "--with-nix" in sys.argv:
    sys.argv.remove("--with-nix")
    with_nix = True
else:
    with_nix = check_nix(library_dirs, include_dirs, compile_args)

if with_nix:
    if boost_lib is None:
        print("Could not find boost python version for {}.{}".format(
            *sys.version_info[0:2]))
        print("Available boost python libs:")
        print("\n".join(map(str, boost_libs)))
        sys.exit(-1)

    libraries.append(boost_lib.library_name)

    extargs = dict(
        extra_compile_args=['-std=c++11']
        if not is_win else ['/DBOOST_PYTHON_STATIC_LIB', '/EHsc'],
        libraries=libraries,
        sources=nixpy_sources,
        runtime_library_dirs=library_dirs if not is_win else None,
    )

    pc = pkg_config("nix", library_dirs=library_dirs,
                    include_dirs=include_dirs, ignore_error=False)
    for k in pc:
        if k in extargs:
            pc[k] = list(set(pc[k] + extargs[k]))
    extargs.update(pc)
    native_ext = Extension('nixio.core', **extargs)
    ext_modules = [native_ext]
else:
    print("Skipping NIX C++ bindings.")
    ext_modules = []

setup(
    name='nixio',
    version=VERSION,
    author=AUTHOR,
    author_email=CONTACT,
    url=HOMEPAGE,
    description=BRIEF,
    long_description=description_text,
    classifiers=classifiers,
    license='BSD',
    ext_modules=ext_modules,
    packages=['nixio', 'nixio.pycore', 'nixio.util',
              'nixio.pycore.util', 'nixio.pycore.exceptions'],
    scripts=[],
    tests_require=['pytest'],
    test_suite='pytest',
    setup_requires=['pytest-runner'],
    install_requires=['numpy', 'h5py'],
    package_data={'nixio': [license_text, description_text]},
    include_package_data=True,
    zip_safe=False,
    data_files=get_wheel_data()
)
