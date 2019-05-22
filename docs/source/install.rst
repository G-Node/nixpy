=======================
Installation Guidelines
=======================

Installation instructions
=========================

The latest stable release of NIXPy is available on PyPi as `nixio`_.
NIXPy works with Python versions 2.7 and 3.6+ on Windows, macOS, and Linux.
The simplest way to install NIXPy is to use pip::

  pip3 install nixio

or for Python 2.7::

  pip2 install nixio

Further mentions of ``pip install`` imply either pip3 or pip2 can be used.

Install developer version
---------------------------
The latest unstable (beta) version of NIXPy at any given time is also on PyPi and can be installed with pip::

  pip install nixio --pre

*Note that this version may contain untested code and should be used for testing new features in the format.*


Build NIXPy from Source
-----------------------

You can also build NIXPy from source, if you want to test changes that are newer than the latest beta release or want to modify the source.
The source code is available on `GitHub`_ and can be built as follows::

  git clone https://github.com/G-Node/nixpy
  python setup.py install

Alternatively, to install in one step using pip::

  pip install git+https://github.com/G-Node/nixpy


Dependencies
============

NIXPy depends on `h5py`_, the Python interface to the HDF5 data format and numpy .

The installation instructions below describe how to build or install NIXPy as a standalone, pure Python version of NIX.

Dependencies:

- h5py: https://pypi.org/project/h5py/
- numpy: https://pypi.org/project/numpy/

.. LINKS
.. _nixio: https://pypi.python.org/pypi/nixio/
.. _Github: https://github.com/G-Node/nixpy/tree/no-bindings-dev
.. _h5py: http://www.h5py.org/
.. _NIXPy: https://github.com/G-Node/nixpy
