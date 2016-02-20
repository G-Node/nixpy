
[![Build Status](https://travis-ci.org/G-Node/nixpy.png?branch=master)](https://travis-ci.org/G-Node/nixpy)
[![Coverage Status](https://coveralls.io/repos/G-Node/nixpy/badge.png?branch=master)](https://coveralls.io/r/G-Node/nixpy?branch=master)

--

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

```
bash
# install dependencies
sudo apt-get install libboost-python-dev build-essential python-dev python-setuptools python-numpy

# clone NIX
git clone https://github.com/G-Node/nixpy
cd nixpy

# build nixpy
python setup.py build

# run the unit tests
python setup.py test

# install
sudo python setup.py install
```

Getting Started (Mac OS X)
-------------------------
**Getting the source code**

Get the source code from GitHub using :

`git clone https://github.com/G-Node/nixpy.git`

**Build NIXPY under OS X**

_Dependecies_

- NIXPY requires installation of [NIX](https://github.com/G-Node/nix). Make sure you install NIX first.
- boost-python.
 Install it using homebrew. `brew install boost-python`
- Python (version = 2.7.x) + python-setuptools + python-numpy (version >= 1.8.0). 

OS X default python works well.

_Instruction to build_

```
bash

# install dependencies if required
sudo apt-get install libboost-python-dev build-essential python-dev python-setuptools python-numpy

# build
python setup.py build

# unit tests
python setup.py test

# install 
sudo python setup.py install
```

**To check if installed properly**

```
bash

python

Python 2.7.11 (default, Dec  5 2015, 14:44:53)
[GCC 4.2.1 Compatible Apple LLVM 7.0.0 (clang-700.1.76)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>>import nix
>>>
```

If python succesfully executes `import nix`, the installation went good.
Check out the API documentation for further tutorials. 



Getting Started (Windows)
-------------------------

**Windows Installer**

You can get a [windows installer](https://github.com/G-Node/nixpy/releases) for both, 32- and 64-bit.

**Build NIXPY under Windows**

To build NIXPY under windows follow the guide provided under: [Win32.md](https://github.com/G-Node/nixpy/blob/master/Win32.md)

NIXPY API Documentation
---------------------

The API documentation can be found [here](http://g-node.github.io/nixpy/)
