.. image:: https://travis-ci.org/G-Node/nixpy.svg?branch=master
    :target: https://travis-ci.org/G-Node/nixpy
.. image:: https://ci.appveyor.com/api/projects/status/8hi7323w3lijr16y/branch/master?svg=true
    :target: https://ci.appveyor.com/project/achilleas-k/nixpy/branch/master
.. image:: https://coveralls.io/repos/github/G-Node/nixpy/badge.svg?branch=master
    :target: https://coveralls.io/github/G-Node/nixpy?branch=master

----

About NIXPY
-----------

The *NIXPY* project is an extension to `NIX <https://github.com/G-Node/nix>`_ and provides Python bindings for *NIX*.

Development Status
------------------

The *NIXPY* project is now in a `beta <https://github.com/G-Node/nixpy/releases>`_ stage and should not be seen as a final product.

Getting Started
---------------

The simplest way to install *NIXPY* is from PyPI using pip. The name of the package is `nixio <https://pypi.python.org/pypi/nixio>`_::

    pip install nixio

Bindings for C++ NIX
--------------------

The setup script will automatically build the bindings for *NIX* if it is detected on the system, otherwise only the pure Python version will be installed.

For instructions on building *NIX*, see the `NIX README <https://github.com/G-Node/nix/blob/master/README.md>`_ file.


To check if installed properly
------------------------------

Try importing nixio::

    >>> import nixio
    >>>

If python successfully executes :code:`import nixio`, the installation went well.
Check out the API documentation for further tutorials.


NIXPY API Documentation
-----------------------

The API documentation can be found `here <http://g-node.github.io/nixpy/>`_.
