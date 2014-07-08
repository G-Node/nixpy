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

Working with Sections
---------------------

TODO some examples for working with sections

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
