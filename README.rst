.. image:: https://github.com/G-Node/nixpy/workflows/NIXPy%20tests%20and%20linting/badge.svg?branch=master
    :target: https://github.com/G-Node/nixpy/actions
.. image:: https://ci.appveyor.com/api/projects/status/72l10ooxbvf0vfgd/branch/master?svg=true
    :target: https://ci.appveyor.com/project/G-Node/nixpy
.. image:: https://coveralls.io/repos/github/G-Node/nixpy/badge.svg?branch=master
    :target: https://coveralls.io/github/G-Node/nixpy?branch=master
.. image:: https://codecov.io/gh/G-Node/nixpy/branch/master/graph/badge.svg?token=xT5rz1BlGJ
    :target: https://codecov.io/gh/G-Node/nixpy


----

Versions
--------

This repository's `master` is the development branch of *NIXPY*. It is not guaranteed to build or work properly. At times it may not even work at all. We strongly recommend using the latest stable version, which can be found on PyPI as nixio_.

About NIXPY
-----------

The *NIXPY* project is an extension to `NIX <https://github.com/G-Node/nix>`_ and provides Python bindings for *NIX*.

Getting Started
---------------

The simplest way to install *NIXPY* is from PyPI using pip. The name of the package is nixio_::

    pip install nixio


To check if installed properly
------------------------------

Try importing nixio::

    >>> import nixio
    >>>

If python successfully executes :code:`import nixio`, the installation went well.
Check out the API documentation for further tutorials.


NIXPY API Documentation
-----------------------

The API documentation can be found `here <https://nixpy.readthedocs.io/>`_.


.. _nixio: https://pypi.python.org/pypi/nixio
