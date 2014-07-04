==========================
API Documentation for Data
==========================

TODO write something about the data model


File
====

A File represents a specific data source of a NIX back-end for example an NIX HDF5 file. All entities of the nix data
model (except the Value entity) must exist in the context of an open File object. Therefore NIX entities can't be
initialized via their constructors but only through the factory methods of their respective parent entity.

Working with files
------------------

.. code-block:: python
   :linenos:

   file = File.open("test.h5", FileMode.ReadWrite)
   # do some work
   file.close()


File open modes
---------------

.. autoclass:: nix.FileMode
    :members:
    :undoc-members:
    :exclude-members: names, values

File API
--------

.. autoclass:: nix.File
    :members:
    :inherited-members:
    :undoc-members:

Block
=====

The Block entity is a top-level, summarizing element that allows to
group the other data entities belonging for example to the same recording session.
All data entities such as Source, DataArray, SimpleTag and
DataTag have to be associated with one Block.

Create a new Block
------------------

A block can only be created on an existing file object. Do not use the blocks constructors for this
purpose.

.. code-block:: python
   :linenos:

   block = file.create_block("session one", "recordingsession");

Working with blocks
-------------------

After a block was created it can be used to create further entities. See the documentation of
Source, DataArray, SimpleTag and DataTag for more information. The next example shows how some
properties of a block can be accessed.

.. code-block:: python
   :linenos:

   block = file.blocks[some_id]

   # set the blocks name
   block.name = "session two"

   # add metadata to a block
   section = file.sections[sec_id]
   block.metadata = section

   # get associated metadata from a block
   block.metadata

   # remove associated metadata from a block
   block.metadata = None

Deleting a block
----------------

When a block is deleted from a file all contained data e.g. sources, data arrays
and tags will be removed too.

.. code-block:: python
   :linenos:

   del file.blocks[some_id]

Block API
---------

.. autoclass:: nix.Block
    :members:
    :inherited-members:
    :undoc-members:

DataArray
=========

Data Types
----------

.. autoclass:: nix.DataType
    :members:
    :undoc-members:
    :exclude-members: names, values


DataArray API
-------------

.. autoclass:: nix.DataArray
    :members:
    :inherited-members:
    :undoc-members:


Source
======

.. autoclass:: nix.Source
    :members:
    :inherited-members:
    :undoc-members:
