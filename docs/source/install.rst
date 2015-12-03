=======================
Installation Guidelines
=======================

Install NIX and other dependencies
==================================

Because NIXPy is build upon the `NIX library`_ it is necessary to install the NIX library before you can install or build NIXPy on your system.
The following two sections explain how NIX can be installed on Windows and Linux.

.. _NIX library: https://github.com/G-Node/nix

Linux
-----

If you use the latest Ubuntu LTS you can install NIX from our `PPA`_ on launchpad.
First you have to add the PPA to your system::

    sudo add-apt-repository ppa:gnode/nix
    sudo apt-get update

Afterwards you can use apt to install the NIX package::

    sudo apt-get install libnix-dev

If you want to use NIX on other distributions you have to compile and install NIX from source.

.. _PPA: https://launchpad.net/~gnode/+archive/ubuntu/nix

Windows
-------

To install NIX under Windows it is recommended to use the latest installer.
The installer can be downloaded from the `nix releases`_ on GitHub.

.. _nix releases: https://github.com/G-Node/nix/releases

Build NIX from Source
---------------------

In order to build and install NIX from source please follow the build instructions in the NIX repository.
Comprehensive build instructions for Linux can be found in the `nix README.md`_.
For Windows this information can be found in the `nix Win32.md`_ file.

.. _nix README.md: https://github.com/G-Node/nix/blob/master/README.md#getting-started-linux
.. _nix Win32.md: https://github.com/G-Node/nix/blob/master/Win32.md

Install NIXPy
=============

Once the `NIX library`_ ist installed on your system you can proceed with the installation of the python bindings.

Compatibility
-------------

The `NIX library`_ as well as NIXPy undergo continuous development and improvement.
Although most changes do not affect the NIX API, the compatibility between the NIX library and their bindings might still break from time to time.
Therefore it is worth mentioning which assumptions can be made concerning compatibility between versions of the NIX projects.

 * The head of the master branches of the NIX library and the bindings are usually compatible to each other.
 * Nix releases of the same version and their corresponding tags in the repositories are always compatible with each other e.g.
   NIXPy 1.0.x is compatible with libnix 1.0.x etc.

Linux
-----

If you use the latest Ubuntu LTS you can install NIXPy the same was as shown above for NIX from our `PPA`_ on launchpad.
If the PPA was not already added to your system, you can do so by executing the following commands:::

    sudo add-apt-repository ppa:gnode/nix
    sudo apt-get update

Once the PPA was added NIXPy can be installed via apt-get::

    sudo apt-get install python-nix

If you want to use NIXPy on other distributions, pleas follow the instructions for building NIXPy from source.

Windows
-------

To install NIXPy under Windows it is recommended to use the Windows installer.
Download the installer with the same version as your NIX installation from the `NIXPy releases`_ and execute the installer.
In addition NIXPy requires numpy to be installed.

.. _NIXPy releases: https://github.com/G-Node/nixpy/releases

Build NIXPy from Source
-----------------------

If you want to use the latest development version or in cases where the provided installers or packages can't be used,
it is possible to build and install NIXPy from sources.
Instructions for building NIX on Linux can be found in the `NIXPy README.md`_ file.
For the Windows platform those instructions are described in the `NIXPy Win32.md`_ file.

.. _NIXPy README.md: https://github.com/G-Node/nixpy/blob/master/README.md#getting-started-linux
.. _NIXPy Win32.md: https://github.com/G-Node/nixpy/blob/master/Win32.md
