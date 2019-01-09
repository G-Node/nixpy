=======================
Installation Guidelines
=======================

Dependencies
============

`NIXPy`_ is a reimplementation of the `NIX`_ library and file format for Python.
NIXPy depends on `h5py`_, the Python interface to the HDF5 data format and numpy .

The installation instructions below describe how to build or install NIXPy as a standalone, pure Python version of NIX.

Dependencies:

- h5py: http://docs.h5py.org/en/latest/build.html
- numpy: https://docs.scipy.org/doc/numpy-1.10.1/user/install.html

.. _NIX: https://github.com/G-Node/nix
.. _h5py: http://www.h5py.org/
.. _NIXPy: https://github.com/G-Node/nixpy


Installation instructions
=========================

The latest release of NIXPy is available on PyPi as `nixio`_.
Therefore, the simplest way to install NIXPy is to use pip::

    pip install nixio --pre

.. _nixio: https://pypi.python.org/pypi/nixio/


.. _advanced installation:


Build NIXPy from Source
-----------------------

If you want to use the latest development version or in cases where the provided installers or packages can't be used,
it is possible to build and install NIXPy from sources from `Github`_::

  git clone https://github.com/G-Node/nixpy.git
  python setup.py install


.. _Github: https://github.com/G-Node/nixpy/tree/no-bindings-dev