About NIXPY
-------------

The *NIXPY* project is an extension to [NIX](https://github.com/G-Node/nix) and provides Python bindings for *NIX*.

Development Status
------------------

The *NIXPY* project is now in a [Beta](https://github.com/G-Node/nixpy/releases) stage and should not be seen as a final product.

Getting Started (Linux)
-----------------------

**Debian PPA**

You can get a ready to install package for Ubuntu "trusty". You have to add & install the following software source to your system:

```
deb http://ppa.launchpad.net/gnode/nix/ubuntu trusty main 
deb-src http://ppa.launchpad.net/gnode/nix/ubuntu trusty main 
```
by executing 

```
sudo add-apt-repository ppa:gnode/nix
sudo apt-get update
sudo apt-get install python-nix
```

**Build NIXPY under Ubuntu 14.04**

_Dependencies_

In order to build the NIXPY library a compiler is needed (gcc, clang). Further nixpy depends on the following libraries:

- Boost (version 1.56 or higher)
- NIX (version 0.10.5 or higher)
- Python (version = 2.7.x) + python-setuptools + python-numpy (version >= 1.8.0)

_Instructions_

```bash
# install dependencies
sudo apt-get install libboost-python-dev build-essential python-dev python-setuptools

# clone NIX
git clone https://github.com/G-Node/nixpy
cd nix

# build nixpy
python setup.py build

# run the unit tests
python setup.py test

# install
sudo python setup.py install
```

Getting Started (Windows)
-------------------------

**Windows Installer**

You can get a windows installer for both, 32- and 64-bit: [nixpy - Beta 1](https://github.com/G-Node/nixpy/releases)

**Build NIXPY under Windows**

To build NIXPY under windows follow the guide provided under: [Win32.md](https://github.com/G-Node/nixpy/blob/master/Win32.md)

NIXPY API Documentation
---------------------

The API documentation can be found [here](http://g-node.github.io/nixpy/)

--

[![Build Status](https://travis-ci.org/G-Node/nixpy.png?branch=master)](https://travis-ci.org/G-Node/nixpy)
[![Coverage Status](https://coveralls.io/repos/G-Node/nixpy/badge.png?branch=master)](https://coveralls.io/r/G-Node/nixpy?branch=master)
