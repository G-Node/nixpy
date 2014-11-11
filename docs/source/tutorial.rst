============== 
NIXPy Tutorial
============== 

In the following you will find tutorials showing how to use nixpy to
read and write nix-files. We will first introduce the design
principles of the nix Data Model. Further down this page, you will
find example programs showing how to store different data types in the
data model how to establish links between entities, add metadata etc..


Design Principles
=================

The design of the data model tries to draw on similarities of
different data types and structures and and come up with *entities*
that are as generic and versatile as meaningful. At the same time we
aim for clearly established links between differen entities to keep the
model as expressive as possible.

Creating a file
"""""""""""""""

So far we have implemented the nix model only for the HDF5 file
format. In order to store data in a file we need to create one.

.. code-block:: python
		
		import nix
		
		nix_file = nix.File.open('example.h5', nix.FileMode.Overwrite)

The **File** entity is the root of this document and it has only two
children the *data* and *metadata* nodes. You may want to use the
hdfview tool to open the file and look at it. Of course you can access
both parts using the **File** API.

All information directly related to a chunk of data is stored in the
*data* node as children of a top-level entity called **Block**. A
**Block** is a grouping element that can represent many things. For
example it can take up everything that was recorded in the same
*session*. Therefore, the **Block** has a *name* and a *type*.

.. code-block:: python

		block = nix_file.create_block("Test block", "nix.session")

Names can be freely chosen. Duplication of names on the same
hierarchy-level is not allowed. In this example creating a second
**Block** with the very same name leads to an error. Names must not
contain '/' characters since they are path separators in the HDF5
file. To avoid collisions across files every created entity has an
unique id (UUID).

.. code-block:: python

		block.id
		'017d7764-173b-4716-a6c2-45f6d37ddb52'


Storing data
"""""""""""" 

The heart of our data model is an entity called **DataArray**. This is
the entity that actually stores all data. It can take n-dimensional
arrays and provides sufficient information to create a basic plot of
the data. To achieve this, one essential parts is to define what kind
of data is stored. Hence, every dimension of the stored data **must**
be defined using the available Dimension descriptors (below). The
following code snippets show how to create an **DataArray** and how to
store data in it.


.. code-block:: python
		
		# create a DataArray and store data in it
		data = block.create_data_array("my data", "nix.sampled", data=some_numpy_array)

Using this call will create a **DataArray**, set name and type, set
the *dataType* according to the dtype of the passed data, and store
the data in the file. You can also create empty **DataArrays** to take
up data-to-be-recorded. In this case you have to provide the space
that will be needed in advance. 

.. code-block:: python
		
		# create an empty DataArray to store 2x1000 values
		data = block.create_data_array("my data", "nix.sampled", dtype=nix.dtype.Double, shape=(2,1000))
		some_numpy_array = np.random.randn(2, 1000)
		data = some_numpy_array


If you do not know the size of the data in advance, you can append
data to an already existing **DataArray**. **Beware:** Though it is
possible to extend the data, it is not possible to change the
dimensionality (rank) of the data afterwards.

.. code-block:: python
		
		# create an empty DataArray to store 2x1000 values
		data = block.create_data_array("my data", "nix.sampled", dtype=nix.dtype.Double, shape=(2,1000))
		some_numpy_array = np.random.randn(2, 1000)
		data[:, :] = some_numpy_array
		some_more_data = np.random.randn(2,10)
		data.data_extent((2,1010))
		data[:, 1000:] = some_more_data


Dimension descriptors
"""""""""""""""""""""

In the above examples we have created **DataArray** entities that are
used to store the data. Goal of our model design is that the data
containing structures carry enough information to create a basic
plot. Let's assume a time-series of data needs to be stored: The data
is just a vector of measurements (e.g. voltages). The data would be
plotted as a line-plot. We thus need to define the x- and the y-axis
of the plot. The y- or value axis is defined by setting the label and
the unit properties of the **DataArray**, the x-axis needs a dimension
descriptor. In the nix model three different dimension descriptors are
defined. **SampledDimension**, **RangeDimension**, and
**SetDimension** which are used for (i) data that has been sampled in
space or time in regular intervals, (ii) data that has been sampled in
irregular intervals, and (iii) data that belongs to categories.

.. code_block:: python

		sample_interval = 0.001 # s
		sinewave = np.sin(np.arange(0, 1.0, sample_interval) * 2 * np.pi)
		data = block.create_data_array("sinewave","nix.regular_sampled",data=sinewave)
		data.label = "voltage"
		data.unit = "mV"
		# define the time dimension of the data
		dim = data.append_sampled_dimension(sample_interval)
		dim.label = "time"
		dim.unit = "s"

The **SampledDimension** can also be used to desribe space dimensions,
e.g. in case of images. 

If the data was sampled at irregular intervals the sample points of
the x-axis are defined using the *ticks* property of a
**RangeDimension**.

.. code_block:: python
		
		sample_times = [1.0, 3.0, 4.2, 4.7, 9.6]
		dim = data.append_range_dimension(sample_times)
		dim.label = "time"
		dim.unit = "s"

Finally, some data belongs into categroies which do not necessarly
have a natural order. In these cases a **SetDimension** is used. This
descriptor can store for each category an optional label.

.. code_block:: python
		
		observations = [0, 0, 5, 20, 45, 40, 28, 12, 2, 0, 1, 0]
		categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
		              'Jul', 'Aug','Sep','Oct','Nov', 'Dec']
		data = block.create_data_array("observations", "nix.histogram", data=observations)
		dim = data.append_set_dimension()
		dim.labels = categories


Annotate regions in the data
""""""""""""""""""""""""""""

TOTO

Adding further information
""""""""""""""""""""""""""

TODO

.. _toc:

List of Tutorials
==========
* Working with files

  * :ref:`working_with_files`

* Basic data structures

  * :ref:`regularly_sampled_data`
  * :ref:`irregularly_sampled_data`
  * :ref:`event_data`
  * :ref:`multiple_signals`
  * :ref:`image_data`

* Tagging points and regions-of-interest

  * :ref:`single_roi`
  * :ref:`multiple_rois`
  * :ref:`spike_tagging`

* Features

  * :ref:`tagged_feature`
  * :ref:`indexed_feature`


.. _working_with_files:

Working with Files
==================

The following code shows how to create a new nix-file, close it and
re-open them with different access rights (examples/fileCreate.py).

.. literalinclude:: examples/fileCreate.py


Source code of this example: `fileCreate.py`_.

.. _fileCreate.py: examples/fileCreate.py

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
		    :lines: 53-66    

.. image:: examples/regular_sampled.png
	   :width: 240

Source code for this example: `regularlySampledData.py`_.

.. _regularlySampledData.py: examples/regularlySampledData.py

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
		    :lines: 57-63 


.. image:: examples/irregular.png
	   :width: 240

Source code for this example: `irregularlySampledData.py`_.

.. _irregularlySampledData.py: examples/irregularlySampledData.py

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
		    :lines: 66-76

.. image:: examples/multiple_time_series.png
	   :width: 240

Source code for this example: `multipleTimeSeries.py`_.

.. _multipleTimeSeries.py: examples/irregularlySampledData.py

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
		    :lines: 59-66

.. image:: examples/lenna.png
	   :width: 240

if the image is not shown install *imagemagick* or *xv* tools (Linux)
Source code for this example: `imageData.py`_.

.. _imageData.py: examples/imageData.py

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
		    :lines: 80-84

.. image:: examples/single_roi.png
	   :width: 240

Source code for this example: `singleROI.py`_.

.. _singleROI.py: examples/singleROI.py

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
		    :lines: 94-107

.. image:: examples/multi_roi.png
	   :width: 240

Source code for this example: `multipleROIs.py`_.

.. _multipleROIs.py: examples/multipleROIs.py

:ref:`toc`

.. _spike_tagging:

Tagging spikes in membrane potential
""""""""""""""""""""""""""""""""""""

Neuroscience example. The same construct as above is used to mark the
times at which action potentials were detected in the recording of a
neuron's membrane potential.

.. literalinclude:: examples/spikeTagging.py
		    :lines: 67-82

.. image:: examples/spike_tagging.png
	   :width: 240

Source code for this example: `spikeTagging.py`_.

.. _spikeTagging.py: examples/spikeTagging.py

:ref:`toc` 

Retrieving tagged regions
"""""""""""""""""""""""""

TODO

:ref:`toc`


Unit support in tagging
"""""""""""""""""""""""

TODO

:ref:`toc`

.. _features:

Features
========

The following code shows how to use the **Features** of the
Nix-model. Suppose that we have the recording of a signal in which a
set of events is detected. No each event may have certain
characteristics one wants to store. These are stored as **Features**
of the events.


.. _untagged_feature:

Untagged Feature
""""""""""""""""

TODO


.. _tagged_feature:

Tagged Feature
""""""""""""""

Tagged **Features** are used in cases in which the positions and
extents of a tag also apply to another linked dataset. In the
following example the spike times should also be applied to the
stimulus that led to the responses. The stimulus is saved in an
additional **DataArray** and is linked to the spike times as a
**Feature** setting the **LinkType** to *tagged*.

.. literalinclude:: examples/taggedFeature.py
		    :lines: 108-122

.. image:: examples/tagged_feature.png
	   :width: 240

Source code for this example: `taggedFeature.py`_.

.. _taggedFeature.py: examples/taggedFeature.py

:ref:`toc` 

Retrieving tagged regions
"""""""""""""""""""""""""

TODO

:ref:`toc`


.. _indexed_feature:

Indexed Feature
"""""""""""""""

In the example, the signal is the membrane potential of a (model)
neuron which was stimulated with some stimulus. The events are again
the action potentials (or spikes) fired by that neuron. A typical
analysis performed on such data is the Spike triggered average which
represent the average stimulus that led to a spike. For each spike, a
snippet of the respective stimulus is cut out and later averaged. In
this example we store these stimulus snippets and link them to the
events by adding a **Feature** to the **MultiTag**. There are three
different flags that define how this link has to be interpreted. In
this case there is one snippet for each spike. The index of each
position has to be used as an index in the first dimension of the
Feature data. The **LinkType** has to be set to *indexed*.

.. literalinclude:: examples/spikeFeatures.py
		    :lines: 135-147

.. image:: examples/spike_feature.png
	   :width: 240

Source code for this example: `spikeFeatures.py`_.

.. _spikeFeatures.py: examples/spikeFeatures.py


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
