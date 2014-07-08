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

The DataArray is the core entity of the NIX data model, its purpose is to
store arbitrary n-dimensional data. In addition to the common fields id,
name, type, and definition the DataArray stores sufficient information to
understand the physical nature of the stored data.

A guiding principle of the data model is provides enough information to create a
plot of the stored data. In order to do so, the DataArray defines a property
dataType which provides the physical type of the stored data (for example
16 bit integer or double precision IEEE floatingpoint number).
The property unit specifies the SI unit of the values stored in the
DataArray whereas the label defines what is given in this units.
Together, both specify what corresponds to the the y-axis of a plot.

In some cases it is much more efficient or convenient to store data not as
floating point numbers but rather as (16 bit) integer values as, for example
read from a data acquisition board. In order to convert such data to the
correct values, we follow the approach taken by the comedi data-acquisition
library (http://www.comedi.org) and provide polynomCoefficients and an
expansionOrigin.

Create and delete a DataArray
-----------------------------

A DataArray can only be created at an existing block. Do not use the
DataArrays constructors for this purpose.

.. code-block:: python
   :linenos:

   data_array = block.crate_data_array("matrix", "data");
   del block.data_arrays[data_array]


DataArray API
-------------

.. autoclass:: nix.DataArray
    :members:
    :inherited-members:
    :undoc-members:

DataSet
=======

The DataSet object is used for data input/output to the underlying storage.

.. autoclass:: nix.data_array.DataSet
    :members:
    :inherited-members:
    :undoc-members:


Tags
====

Besides the DataArray the tag entities can be considered as the other
core entities of the data model.
They are meant to attach annotations directly to the data and to establish meaningful
links between different kinds of stored data.
Most importantly tags allow the definition of points or regions of interest in data
that is stored in other DataArray entities. The data array entities the
tag applies to are defined by its property references.

Further the referenced data is defined by an origin vector called position
and an optional extent vector that defines its size.
Therefore position and extent of a tag, together with the references field
defines a group of points or regions of interest collected from a subset of all
available DataArray entities.

Further tags have a field called features which makes it possible to associate
other data with the tag.  Semantically a feature of a tag is some additional data that
contains additional information about the points of hyperslabs defined by the tag.
This could be for example data that represents a stimulus (e.g. an image or a
signal) that was applied in a certain interval during the recording.

SimpleTag API
-------------

.. autoclass:: nix.SimpleTag
    :members:
    :inherited-members:
    :undoc-members:

DataTag API
-------------

.. autoclass:: nix.DataTag
    :members:
    :inherited-members:
    :undoc-members:

Source
======

.. autoclass:: nix.Source
    :members:
    :inherited-members:
    :undoc-members:
