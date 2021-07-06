.. toctree::
    :maxdepth: 1

.. _metadata:

Annotations with arbitrary metadata
===================================

The entities of the data model that were discussed so far carry just enough information to get a basic understanding of the stored data. Often much more information than that is required. Storing additional metadata is a central part of the NIX concept. We use a slightly modified version of the *odML* data model for metadata to store additional information. In brief: the model consists of *Sections* that contain *Properties* which in turn carry a list of values. Again, *Sections* can be nested to represent logical dependencies in the hierarchy of a tree. While all data entities discussed above are children of *Block* entities, the metadata lives parallel to the *Blocks*. The idea behind this is that several blocks may refer to the same metadata, or, the other way round the metadata applies to data entities in several blocks. The *types* used for the *Sections* in the following example are defined
in the `odml terminologies <https://github.com/G-Node/odml-terminologies>`_

Most of the data entities can link to metadata sections.

.. literalinclude:: examples/annotations.py
    :lines: 5-21
    :caption: We can add arbitrary metadata in trees of *Sections* and *Properties* (:download:`example code <examples/annotations.py>`).

For a quick view of the metadata tree pretty-print it:

.. literalinclude:: examples/annotations.py
    :lines: 24

which leads to an output like this. The argument ``max_depth=-1`` notes that the full depth of the tree should be displayed. In the default case (``max_depth=1``) the display will be more compact and will not recursively traverse the whole tree. 

.. code-block:: text

    recording session [odml.recording]
        |- experimenter: ('John Doe',)
        |- recording date: ('2014-01-01',)
    subject [odml.subject]
        |- id: ('mouse xyz',)
        cell [odml.cell]
            |- resting potential: (-64.5,)mV

The *Sections* add much like dictionaries. To access e.g. the "resting potential" of the cell we may call:

.. literalinclude:: examples/annotations.py
    :lines: 26

Extending Properties
--------------------

Properties can carry multiple values and additional information such as a definition. 

.. literalinclude:: examples/annotations.py
    :lines: 33-35

Reading the values will return a tuple. This has the background that one cannot change a tuple. Changing the values stored in a *Property* can be done e.g. by the ``extend_values`` method

.. literalinclude:: examples/annotations.py
    :lines: 37-38

One can extend it by single values or by lists of values. 

The data type of all values must, however, be the same. Adding a number to the list of strings will fail with a ``TypeError``:

.. literalinclude:: examples/annotations.py
    :lines: 40-43

.. code-block:: text

    New data type '<class 'numpy.int64'>' is inconsistent with the Property's data type '<class 'numpy.str_'>'

**Note:** Once the property has been created, the data type can't be changed. One would need to create a replacement with the desired data type.

Finding annotations
-------------------

If we do not know the exact path of the *Section* we are looking for, we need to search it by passing a function (in this case a lambda function) to the ``find_section`` method. The following code shows two examples in which we look first for a section with a given name or second a section which contains a property with a certain name. 

.. literalinclude:: examples/annotations.py
    :lines: 28 - 31

The result of the ``find_sections`` will always be a list which may be empty if no match was found. Therefore, the call in the last line is to some extent risky and would lead to an ``OutOfBounds`` exception if the search failed.
