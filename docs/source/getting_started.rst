Introduction to *NIX*
=====================

This introduction guides through the *NIX*
data model and shows how to use it with the `nixio
python library <https://github.com/g-node/nixpy>`__.

---------------

In the following we provide an introduction to the general concepts of
the *NIX* data model, try to illustrate its design principles and
provide code examples showing the usage of the
`python <https://github.com/g-node/nixpy>`__ library for reading and writing
*NIX* files.

Code examples use the python library but almost all functions have direct
counterparts also in the `C++ library <https://github.com/g-node/nix>`__
or the language bindings to this for
`Matlab <https://github.com/g-node/nix-mx>`__ and
`java <https://github.com/g-node/nix-java>`__.

Basic idea
==========

The basic idea of the *NIX* project is to come up with a **generic**
data model that defines as few structures/entities as possible while
being able to represent a multitude of different data structures, allows
for in-depth annotation and supports standardization.

Designing a **generic** data model implies that the defined entities are
named in a way that may seem uncommon but are more general than the
*domain-specific* terms used in any given field or community.

The idea of the *NIX* data model has been implemented using the
`HDF5 <https://www.hdfgroup.org>`__ file format.

---------

Tutorials
=========

Most code examples are standalone and you should be able to run them. The code is also available from the `project repository on GitHub <https://github.com/G-Node/nixpy/tree/master/docs/source/examples>`_.

.. toctree::
   file_handling
   storing_data
   tagging
   data_handling
   annotating
   standardization
   finding_things
   image_data
   spike_time_data
   :maxdepth: 1