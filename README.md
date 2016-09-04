
[![Build Status](https://travis-ci.org/G-Node/nixpy.png?branch=master)](https://travis-ci.org/G-Node/nixpy)
[![Coverage Status](https://coveralls.io/repos/G-Node/nixpy/badge.png?branch=master)](https://coveralls.io/r/G-Node/nixpy?branch=master)

--

About NIXPY
-----------

The *NIXPY* project is an extension to [NIX](https://github.com/G-Node/nix) and provides Python bindings for *NIX*.

Development Status
------------------

The *NIXPY* project is now in a [Beta](https://github.com/G-Node/nixpy/releases) stage and should not be seen as a final product.

Getting Started
---------------

The simplest way to install *NIXPY* is from PyPI using pip. The name of the package is [nixio](https://pypi.python.org/pypi/nixio).

```
pip install nixio
```

Bindings for C++ NIX
--------------------

The setup script will automatically build the bindings for *NIX* if it is detected on the system, otherwise only the pure Python version will be installed.

For instructions on building *NIX*, see the [NIX README](https://github.com/G-Node/nix/blob/master/README.md) file.


To check if installed properly
------------------------------

Try importing nixio.

```
>>>import nixio
>>>
```

If python successfully executes `import nixio`, the installation went well.
Check out the API documentation for further tutorials.


NIXPY API Documentation
---------------------

The API documentation can be found [here](http://g-node.github.io/nixpy/).
