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
intervals in space, time, or something else. Let's consider a signal
that has been digitized usind an AD-Converter at a fixed sampling
rate. In this case the axis representing time has to be described
using a **SampledDimension**. This dimension descriptor contains as
mandatory element the *sampling_interval*. The *sampling_interval* has
to be given because it also applies e.g. to spatial sampling, it is
the more general term than the sampling rate which may appear
appropriate for time discretization. Further, the *unit* in which this
number has to be interpreted and a *label* for the axis can be
specidfied. The following code illustrates how this is stored in nix
files.

.. literalinclude:: examples/regularlySampledData.py

.. image:: examples/regular_sampled.png
	   :width: 120

.. _irregularly_sampled_data:

Irregularly sampled data
""""""""""""""""""""""""

Irregularly sampled data is sampled at irregular intervals. The
dimension which is sampled in this way has to be described using a
**RangeDimension**. This dimension descriptor stores besides the
*unit* and *label* of the axis the ticks, e.g. timestamps of the
instances at which the samples were taken.

.. literalinclude:: examples/irregularlySampledData.py

.. image:: examples/irregular.png
	   :width: 120

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
