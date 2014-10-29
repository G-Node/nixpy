============== 
NIXPy Tutorial
============== 

In the following you will find some tutorials showing how to use nixpy
to read and write nix-files. All code can be found in the examples
folder.

.. _toc:

Table of contents
=================

Basic data structures
"""""""""""""""""""""
* :ref:`regularly_sampled_data`
* :ref:`irregularly_sampled_data`
* :ref:`event_data`
* :ref:`multiple_signals`
* :ref:`image_data`

Tagging points and regions-of-interest
""""""""""""""""""""""""""""""""""""""

* :ref:`single_roi`
* :ref:`multiple_rois`
* :ref:`spike_tagging`

Design Principles
=================

TODO write something


Working with Files
==================

The following code shows how to create a new nix-file, close it and
re-open them with different access rights (examples/fileCreate.py).

.. literalinclude:: examples/fileCreate.py

:ref:`toc`

Basic data structures
=====================

In this section we will show how different kinds of data are stored in
nix files. We will start with simple regularly and irregularly sampled
signals, turn to series of such signals and end with images stacks.


.. _regularly_sampled_data:

Regularly sampled data 
"""""""""""""""""""""" 

Regularly sampled data is everything which is sampled in regular
intervals in space, time, or something else. Let's consider a signal
that has been digitized using an AD-Converter at a fixed sampling
rate. In this case the axis representing time has to be described
using a **SampledDimension**. This dimension descriptor contains as
mandatory element the *sampling_interval*. The *sampling_interval* has
to be given because it also applies e.g. to spatial sampling, it is
the more general term than the sampling rate which may appear
appropriate for time discretization. Further, the *unit* in which this
number has to be interpreted and a *label* for the axis can be
specified. The following code illustrates how this is stored in nix
files.

.. literalinclude:: examples/regularlySampledData.py

.. image:: examples/regular_sampled.png
	   :width: 240

:ref:`toc`

.. _irregularly_sampled_data:

Irregularly sampled data
""""""""""""""""""""""""

Irregularly sampled data is sampled at irregular intervals. The
dimension which is sampled in this way has to be described using a
**RangeDimension**. This dimension descriptor stores besides the
*unit* and *label* of the axis the ticks, e.g. time-stamps of the
instances at which the samples were taken.

.. literalinclude:: examples/irregularlySampledData.py

.. image:: examples/irregular.png
	   :width: 240

:ref:`toc`

.. _event_data:

Event data
""""""""""""""""""

TODO


.. _multiple_signals:

Series of signals
"""""""""""""""""

It is possible to store multiple signals that have the same shape and
logically belong together in the same *DataArray* object. In this
case, the data is two-dimensional and two dimension-descriptors are
needed. Depending on the layout of the data one dimension represents
time and is described with a *SampledDimension* while the other
represents the various signals. This is described with a
*SetDimension*. A *SetDimension* can have labels for each entry along
this dimension of the data.

.. literalinclude:: examples/multipleTimeSeries.py

.. image:: examples/multiple_time_series.png
	   :width: 240


:ref:`toc`

.. _image_data:

Image data
""""""""""

Color images can be stored as 3-D data in a *DataArray*. The first two
dimensions represent *width* and *height* of the image while the 3rd
dimension represents the color channels. Accordingly, we need three
dimension descriptors. The first two are *SampledDimensions* since the
pixels of the image are regularly sampled in space. The third
dimension is a *SetDimension* with labels for each of the channels.
In this tutorial the "Lenna" image is used. Please see the author
attribution in the code.

.. literalinclude:: examples/imageData.py

.. image:: examples/lenna.png
	   :width: 240

if the image is not shown install *imagemagick* or *xv* tools (Linux)

:ref:`toc`

Tagging regions
===============

One key feature of the nix-model is its ability to annotate, or "tag",
points or regions-of-interest in the stored data. This feature can be
used to state the occurrence of events during the recording, to state
the intervals of a certain condition, e.g. a stimulus presentation, or
to mark the regions of interests in image data. In the nix data-model
two types of Tags are discriminated. (1) the **Tag** for single points
or regions, and (2) the **MultiTag** to annotate multiple points or
regions using the same entity.

.. _single_roi:

Single point or region
""""""""""""""""""""""

Single points of regions-of-interest are annotated using a **Tag**
object. The Tag contains the start *position* and, optional, the
*extent* of the point or region. The link to the data is established
by adding the **DataArray** that contains the data to the list of
references. It is important to note that *position* and *extent* are
arrays with the length matching the dimensionality of the referenced
data. The same Tag can be applied to many references as long as
*position* and *extent* can be applied to these.

.. literalinclude:: examples/singleROI.py

.. image:: examples/single_roi.png
	   :width: 240

:ref:`toc`

.. _multiple_rois:

Multiple points or regions
""""""""""""""""""""""""""

For tagging multiple regions of interest in the same data the
**MultiTag** object is used. Unlike the simple **Tag** from the
previous example, the multiple *positions* and *extents* can be
given. These are stored in **DataArray** objects. The tagged dataset
is linked via the references.  There are some restrictions regarding
the **DataArrays** storing positions and extents. The data stored in
them **must** be 2-dimensional. Both dimensions are **SetDimensions**
representing the individual positions and the positions in the
referenced data, respectively. Thus, the second dimension has as many
entries as the referenced data has dimensions.

In the following example we will declare multiple ROIs in a image. The
image as a spatial extent and three color channels, is hence 3-D. The
same mechanism can, of course, be used to tag other event in different
kinds of data. For example in the neuroscience context: the detection
of action potentials in a recorded membrane potential.

.. literalinclude:: examples/multipleROIs.py

.. image:: examples/multi_roi.png
	   :width: 240

:ref:`toc`

.. _spike_tagging:

Tagging spikes in membrane potential
""""""""""""""""""""""""""""""""""""

Neuroscience example. The same construct as above is used to mark the
times at which action potentials were detected in the recording of a
neuron's membrane potential.

.. literalinclude:: examples/spikeTagging.py

.. image:: examples/spike_tagging.png
	   :width: 240

:ref:`toc` 

Retrieving tagged regions
"""""""""""""""""""""""""

TODO

:ref:`toc`


Unit support in tagging
"""""""""""""""""""""""

TODO

:ref:`toc`


Using Features
""""""""""""""

TODO

:ref:`toc`


Storing the origin of data
==========================

TODO adding Sources and nesting them

:ref:`toc`

Working with Data
=================

TODO write something

:ref:`toc`


Working with Metadata
=====================

TODO write something

:ref:`toc`
