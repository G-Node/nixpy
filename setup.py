#!/usr/bin/env python
import sys
import os
import json
from setuptools import setup

__author__ = 'Christian Kellner, Achilleas Koutsou'


with open('README.rst') as f:
    description_text = f.read()

with open('LICENSE') as f:
    license_text = f.read()


is_win = os.name == 'nt'

# load info from nixio/info.json
with open(os.path.join("nixio", "info.json")) as infofile:
    infodict = json.load(infofile)

VERSION = infodict["VERSION"]
AUTHOR = infodict["AUTHOR"]
CONTACT = infodict["CONTACT"]
BRIEF = infodict["BRIEF"]
HOMEPAGE = infodict["HOMEPAGE"]


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


classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: Scientific/Engineering'
]

packages = ['nixio',
            'nixio.hdf5',
            'nixio.util',
            'nixio.exceptions',
            'nixio.cmd']


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
    packages=packages,
    scripts=[],
    tests_require=['pytest'],
    test_suite='pytest',
    setup_requires=['pytest-runner'],
    install_requires=['numpy', 'h5py', 'six', 'enum34;python_version<"3.4"'],
    package_data={'nixio': [license_text, description_text]},
    include_package_data=True,
    zip_safe=False,
    data_files=get_wheel_data(),
    entry_points={'console_scripts': [
        'nixio-validate=nixio.cmd.validate:main',
        'nixio-upgrade=nixio.cmd.upgrade:main',
        'nixio-explore=nixio.cmd.nixexplore:main',
    ]}
)
