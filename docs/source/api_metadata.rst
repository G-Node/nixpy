==============================
API Documentation for Metadata
==============================

The model for storing metadata is largely equivalent to the `odML`_ (open metadata Markup Laguage) model. In brief: the
model consists of so called Properties that contain Values much like a key-value pair (plus some additional fields).
These Properties can be grouped into Sections which themselves can be nested to built a tree-structure. Sections are
defined by a name and a type (e.g. a stimulus-type section will contain information that is related to a stimulus).
The basic feature of the odML approach is that it defines the model but not the items that are described or the terms
that are used in this. On the other hand where standardization is required each Section can be based on an
odML-terminology that standardizes without restricting to the terms defined within the terminology.

.. _odML: http://www.frontiersin.org/Neuroinformatics/10.3389/fninf.2011.00016

Section
=======

Metadata stored in a NIX file can be accessed directly from an open file.

Create and delete sub sections
------------------------------

.. code-block:: python
   :linenos:

   sub = section.create_section("a name", "type")
   del section.sections[sub]

Add and remove properties
-------------------------

Properties  can be created using the create_property method. Existing properties can be accessed and deleted
directly from the respective section.

.. code-block:: python
   :linenos:

   section.create_property("one", [Value(1)])
   section.create_property("two", [Value(2)])

   # iterate over properties
   for p in section:
      print(p)

   # access by name
   one = section["one"]

   # convert properties into a dict
   dct = dict(section.items())

   # delete properties
   del section["one"]
   del section["two"]
   
Section API
-----------

.. autoclass:: nix.Section
    :members:
    :inherited-members:
    :undoc-members:

Property
========

.. autoclass:: nix.Property
    :members:
    :inherited-members:
    :undoc-members:

Value
=====

.. autoclass:: nix.Value
    :members:
    :inherited-members:
    :undoc-members:
