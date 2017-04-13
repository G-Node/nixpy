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
    packages=['nixio', 'nixio.hdf5', 'nixio.util', 'nixio.exceptions'],
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
