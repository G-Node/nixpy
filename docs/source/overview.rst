======== 
Overview
======== 

Design Principles
=================

The design of the data model tries to draw on similarities of
different data types and structures and and come up with *entities*
that are as generic and versatile as meaningful. At the same time we
aim for clearly established links between differen entities to keep the
model as expressive as possible. 

Most entities of the NIX-model have a *name* and a *type* field which
are meant to provide information about the entity. While the name can
be freely chose, the type is meant to provide semantic information
about the entity and we aim at definitions of different types. Via the
type, the generic entities can become domain specific.

For the electrophysiology disicplines of the neurosciences, an INCF
working groups has set out to define such data types. For more
information see `here
<http://crcns.org/files/data/nwb/ephys_requirements_v0_72.pdf>`_


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

.. code-block:: python

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

.. code-block:: python
		
		sample_times = [1.0, 3.0, 4.2, 4.7, 9.6]
		dim = data.append_range_dimension(sample_times)
		dim.label = "time"
		dim.unit = "s"

Finally, some data belongs into categroies which do not necessarly
have a natural order. In these cases a **SetDimension** is used. This
descriptor can store for each category an optional label.

.. code-block:: python
		
		observations = [0, 0, 5, 20, 45, 40, 28, 12, 2, 0, 1, 0]
		categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
		              'Jul', 'Aug','Sep','Oct','Nov', 'Dec']
		data = block.create_data_array("observations", "nix.histogram", data=observations)
		dim = data.append_set_dimension()
		dim.labels = categories


Annotate regions in the data
""""""""""""""""""""""""""""

Annotating points of regions of interest is one of the key features of
the nix data-model. There are two entities for this purpose: (i) the
**Tag** is used for single points or regions while the (ii)
**MultiTag** is used to mark multiple of these. Tags have one or many
*positions* and *extents* which define the point or the region in the
*referenced* DataArray. Further they can have **Features** to store
additional information about the positions (see tutorials below).


Tag
---

The tag is a relatively simple structure directly storing the
*position* the tag points and the, optional, *extent* of this
region. Each of these are vectors of a length matching the
dimensionality of the referenced data.

.. code-block:: python
		
		position = [10, 10]
		extent = [5, 20]
		tag = block.create_tag('interesting part', 'nix.roi', position)
		tag.extent = extent
		# finally, add the referenced data to this tag
		tag.references.add(data)


MuliTag
-------

**MultiTags** are made to tag multiple points (regions) at once. The
main difference to the **Tag** is that position and extent are stored
in **DataArray** entities. These entities **must** be 2-D. Both
dimensions are *SetDimensions*. The first dimension represents the
individual positions, the second dimension takes the coordinates in
the referenced n-dimensional **DataArray**.

.. code-block:: python

		# fake data
		frame = np.random.randn((100,100))
		data = block.create_data_array('random image', 'nix.image', data=frame)
		dim_x = data.append_sampled_dimension(1.0)
		dim_x.label = 'x'
		dim_y = data.append_sampled_dimension(1.0)
		dim_y.label = 'y'
		# positions array must be 2D
		p = np.zeros(3,2) # 1st dim, represents the positions, 2nd the coordinates
		p[1,:] = [10,10]
		p[2,:] = [20,10]
		positions = block.create_data_array('special points', 'nix.positions', data=p)
		positions.append_set_dimension()
		dim = positions.append_set_dimension()
		dim.labels = ['x', 'y']
		# create a multi tag
		tag = block.create_multi_tag('interesting points', 'nix.multiple_roi', positions)
		tag.references.append(data)
		

Adding further information
""""""""""""""""""""""""""

The tags establish links between datasets. If one needs to attach
further information to each of the regions defined by the tag, one can
add **Features** to them. A **Feature** references a **DataArray** as
its *data* and specifies with the *link_type* how the link has to be
interpreted.  The *link_type* can either be *tagged*, *indexed*, or
*untagged* indicating that the tag should be applied also to the
feature data (*tagged*), for each position given in the tag, a slice
of the feature data (ith index along the first dimension) is the
feature (*indexed*), or all feature data applies for all positions
(*untagged*).

Let's say we want to give each  point a name, we can create a feature like this:

.. code-block:: python

		spot_names = block.create_data_array('spot ids', 'nix.feature', data=['a', 'b'])
		spot_names.append_set_dimension()
		feature = tag.create_feature(spot_names, nix.LinkType.Indexed)

We could also say that each point in the tagged data (e.g. a matrix of
measurements) has a corresponding point in an input matrix.

.. code-block:: python
		
		input_matrix = np.random.randn(data.shape)
		input_data = block.create_data_array('input matrix', 'nix.feature', data=input_matrix)
		dim_x = input_data.append_sampled_dimension(1.0)
		dim_x.label = 'x'
		dim_y = input_data.append_sampled_dimension(1.0)
		dim_y.label = 'y'
		tag.create_feature(input_data, nix.LinkType.Tagged)


Finally, one could need to attach the same information to all
positions defined in the tag. In this case the feature is *untagged*

.. code-block:: python
		
		common_feature = block.create_data_array('common feature', 'nix.feature', data=some_common_data)
		tag.create_feature(common_feature, nix.LinkType.Untagged)


Defining the Source of the data
"""""""""""""""""""""""""""""""

In cases in which we want to store where the data originates
**Source** entities can be used. Almost all entities of the NIX-model
can have **Sources**. For example, if the recorded data originates
from experiments done with one specific experimental
subject. **Sources** have a name and a type and can have some
definition.

.. code-block:: python

		subject = block.create_source('subject A', 'nix.experimental_subject')
		subject.definition = 'The experimental subject used in this experiment'
		data.sources.append(subject)
		
**Sources** may depend on other **Sources**. For example, in an
electrophysiological experiment we record from different cells in the
same brain region of the same animal. To represent this hierarchy,
**Sources** can be nested, create a tree-like structure.

.. code-block:: python

		subject.block.create_source('subject A', 'nix.experimental_subject')
		brain_region = subject.create_source('hippocampus', 'nix.experimental_subject')
		cell_a = brain_region.create_source('Cell 1', 'nix.experimental_subject')
		cell_b = brain_region.create_source('Cell 2', 'nix.experimental_subject')
			

Arbitrary metadata
""""""""""""""""""

The entities discussed so far carry just enough information to get a
basic understanding of the stored data. Often much more information
than that is required. Storing additional metadata is a central part
of the NIX concept. We use a slightly modified version of the *odML*
data model for metadata to store additional information. In brief: the
model consists of **Sections** that contain **Properties** which in
turn contain one or more **Values**. Again, **Sections** can be nested
to represent logical dependencies in the hierarchy of a tree. While
all data entities discussed above are children of **Block** entities,
the metadata lives parallel to the **Blocks**. The idea behind this is
that several blocks may refer to the same metadata, or, the other way
round the metadata applies to data entities in several blocks. The
*types* used for the **Sections** in the following example are defined
in the `odml terminologies
<https://github.com/G-Node/odml-terminologies>`_

Most of the data entities can link to metadata sections.

.. code-block:: python

		sec = nix_file.create_section('recording session', 'odml.recording')
		sec.create_property('experimenter', nix.Value('John Doe'))
		sec.create_property('recording date', nix_Value('2014-01-01'))
		subject = sec.create_section('subject', 'odml.subject')
		subject.create_property('id', nix.Value('mouse xyz'))
		cell = subject.create_section('cell', 'odml.cell')
		v = nix.Value(-64.5)
		v.uncertainty = 2.25
		p = cell.create_property('resting potential', v)
		p.unit = 'mV'
		# set the recording block metadata
		block.metadata = sec


Units
"""""

In NIX we accept only SI units (plus dB, %) wherever units can be
given. We also accept compound units like *mV/cm*. Units are most of
the times handled transparently. That is, when you tag a region of
data that has been specified with a time axis in seconds and use
e.g. the *tag.retrieve_data* method to get this data slice, the API
will handle unit scaling. The correct data will be returned even if
the tag's position is given in *ms*.


.. code-block:: python

		x_positions=[2,4,6,8,10,12]
		tag=block.create_tag('unit example','nix.sampled',x_positions)
		
		#single SI unit is supported like mV,cm etc.
		tag.units="cm"
		
		#for compound units we can make list
		tag.units=["mV","cm"]
		
		#we can make a compound_unit attribute to get the compound units
		#result will show : mV/cm
		tag.compound_unit = "/".join(tag.units)
