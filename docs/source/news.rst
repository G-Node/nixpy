##################
NEW in version 1.5
##################

With version 1.5 we introduced several changes on the library as well as on the data model side (nix model version 1.2). Some are even breaking changes.
1.5 libraries can open files that have been written with pre 1.5 libraries. Old files cannot be opened for ReadWrite access.
You may want to convert such files using the ``nixio`` command line tool that comes with the library.

.. code-block:: bash
   nixio upgrade --help

Model changes
#############

* the metadata model was simplified and reflects the changes introduced to the underlying **odml** data model.
* New *DataFrame* entity
* *Tags* and *MultiTags* can link to DataFrames as features.
* *RangeDimension* can link to DataFrames as source for the ticks.

The *DataFrame*


The *DataFrame* is a table structure. Each column has a name, unit, and data type. (see xxx for more information)

*RangeDimension*
----------------

*RangeDimensions* ticks can now be stored within the dimension descriptor, or in linked DataArrays or DataFrames. Ticks are still one-dimensional. (see xxx for more information)

API changes
-----------


Misc
****

Extended command line tool abilities; The ``nixio`` command line tool now bundles commands for validating files, upgrading old files to the current version, and to explore file content.

.. code-block:: bash
   nixio --help
