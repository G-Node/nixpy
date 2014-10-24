============== 
NIXPy Tutorial
============== 

In the following you will find some tutorials showing how to use nixpy
to read and write nix-files. All code can be found in the examples
folder.

Tutorials
"""""""""
* :ref:`regularly_sampled_data`
* :ref:`irregularly_sampled_data`
* Series of regularly sampled data 
* Image stacks


Design Principles
=================

TODO write something

Working with Files
==================

The following code shows how to create a new nix-file, close it and
re-open them with different access rights (examples/fileCreate.py).

.. literalinclude:: examples/fileCreate.py

Storing data
============

In this section we will show how different kinds of data are stored in
nix files. We will start with simple regularly and irregularly sampled
signals, turn to series of such signals and end with images stacks.


.. _regularly_sampled_data:

Regularly sampled data 
"""""""""""""""""""""" 

Regularly sampled data is everything which is sampled in regular
intervals in space, time, or something else. The following code
illustrates how this is stored in nix files.

.. literalinclude:: examples/regularlySampledData.py


.. _irregularly_sampled_data:

Irregularly sampled data
""""""""""""""""""""""""

TODO

Series of signals
"""""""""""""""""

TODO

Image stacks
""""""""""""

TODO

Tagging regions
===============

Single Point or region
""""""""""""""""""""""
 TODO

Multiple points or regions
""""""""""""""""""""""""""
 TODO

Working with Data
=================

TODO write something

Working with Metadata
=====================

TODO write something
