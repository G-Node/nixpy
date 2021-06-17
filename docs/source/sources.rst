Noting the origin of data
=========================

In cases in which we want to store where the data originates from *Source* entities can be used. Almost all entities of the NIX-model can have *Sources*. For example, if the recorded data originates from experiments done with one specific experimental
subject.

*Sources* have a name and a type and can have some definition and link to further :ref:`metadata<metadata>`.

.. literalinclude:: examples/sources.py
    :lines: 9-10, 16-19
    :caption: Sources are used to note the origin of the data (:download:`example code <examples/sources.py>`). 
    

*Sources* may depend on other *Sources*. For example, in an electrophysiological experiment we record from different cells in the same brain region of the same animal. To represent this hierarchy, *Sources* can be nested, create a tree-like structure.

.. literalinclude:: examples/sources.py
    :lines: 12 - 16, 23, 27 
    :caption: Sources are used to note the origin of the data (:download:`example code <examples/sources.py>`). 

As mentioned above the Sources build a tree. The block (as the root of the tree) at the moment has only a single source attached to it 

.. literalinclude:: examples/sources.py
    :lines: 53 - 55 

The output should yield:

.. code-block:: text

    block sources: [Source: {name = subject A, type = nix.experimental_subject}]
    subject sources: [Source: {name = hippocampus, type = nix.experimental_subject.subject}]
    brain region sources: [Source: {name = Cell 1, type = nix.experimental_subject.cell}, Source: {name = Cell 2, type = nix.experimental_subject.cell}]

Search and find
---------------

In a data-centered search we can then ask the *DataArray* for it's *Source* to get information about the cell and get the linked metadata. A *DataArray* may have several sources attached to it. To make sure we get the right one (with the cell information) we performa a search on the sources using the **type** information.

.. literalinclude:: examples/sources.py
    :lines: 59 - 61 

The output should give

.. code-block:: text

    Source: Source: {name = Cell 1, type = nix.experimental_subject.cell}
    Source metadata:
    Cell 1 [odml.cell]
        |- Type: ('pyramidal',)
        |- BrainSubregion: ('CA1',)
        |- BaselineRate: (15,)Hz
        |- Layer: ('4',)

In a or source-centered search we can ask for the *DataArrays* that link to a source.

.. literalinclude:: examples/sources.py
    :lines: 63 

This should return a list with a single entry:

.. code-block:: text

    [DataArray: {name = cell a data, type = nix.sampled.time_series}]
