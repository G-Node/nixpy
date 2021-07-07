.. toctree::
   :maxdepth: 1

Finding things
==============

NIX provides features to store data in a way that makes it
understandable and discoverable by others. For example, **Name** and
**Type** fields of the entities should help the human reader to find
their ways through the file and make sense of the stored content and
the relations between entities.

Still, reading a *NIX* file that has been created by another person or
has been automatically written by a recording tool such
as [relacs](https://github.com/relacs/relacs) might be confusing at
first. The following recommendation should help you when exploring an
unknown file.

Recommendations when opening an unknown NIX file
------------------------------------------------

1. Find out how many *Blocks* are stored and try to understand what they
   stand for. In most cases there will be only one *Block* and in the
   `relacs <https://github.com/relacs/relacs>`__ use-case it will
   represent the recordings made on a single neuron.
2. Within the *Block* look for *Group* entities. As indicated by the
   name, these group other entities and thus indicate some kind of
   common relation between the members of each group.
3. Within *Group*\ s or, if there are no *Group*\ s, within the *Block*
   look out for *Tag*\ s and *MultiTag*\ s. These link between data
   carrying *DataArrays* and provide semantic background.
4. For example, a *MultiTag* that has a type “stimulus_segment” quite
   clearly indicates that it highlights periods during which a stimulus
   was presented.
5. For *Tag*\ s and *MultiTag*\ s take a look at the **references**
   which list all *DataArrays* that are tagged. One may further
   investigate the **features** which should provide more information on
   the tagged regions.
6. Almost all entities can link to additional **metadata** that should
   contain information about the stored data.

Standardization helps
---------------------

Having a well-defined data model and the respective API store and
annotate scientific data with related metadata is a huge step toward standardization
and reusability.  As mentioned [before](./standardization.md), if the
file is created according to known definitions, finding stuff in an
unknown file is considerably simplified.

For example, in case one looks for the voltage recording made on the
first channel and it is further known that the file is created e.g. by
`relacs <https://github.com/relacs/relacs>`__ then one needs to look for
“relacs.data.sampled.V-1” typed *DataArray*\ s:

.. code:: python

    nixfile = nixio.File.open("relacs_example.nix", nixio.FileMode.ReadOnly);
    block = f.blocks()[0];
    arrays = [da for da in block.data_arrays if "relacs.data.sampled.v-1" in da.type.lower()]

With this kind of list comprehensions a large variety of searches can be easily performed. The above said assumes a “data-centered” view. The other way would be to
assume a “metadata-centered” view, to scan the metadata tree and
perform an inverse search from the metadata to the data entities that
refer to the respective section. Accordingly, ``Section`` and ``Sources`` define
methods to get the referring *DataArray*\ s, *Tag*\ s, etc..

.. code:: python

    s = nixfile.sections()[0]
    blocks = s.referring_blocks()
    for b in blocks:
        print(b)
