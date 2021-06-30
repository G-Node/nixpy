######################
Changes in version 1.5
######################

With version 1.5 we introduced several changes on the library as well as on the data model side (nix model version 1.2). Some are even breaking changes.
1.5 libraries can open files that have been written with pre 1.5 libraries. Old files cannot be opened for ``ReadWrite`` access.
You may want to convert such files using the ``nixio`` command line tool that comes with the library or via also implement upgrade into a script.

.. code-block:: bash

   nixio upgrade --help

.. code-block:: python

    import nixio
    filename = "test.nix"
    nixio.file_upgrade(filename, quiet=False)

Pass ``quiet=False`` in order to get some feedback on what the tool did. **Note** Files are replaced *in place*. Make sure to backup your files before upgrading.

Model changes
#############

* the metadata model was simplified to reflects the changes introduced to the underlying **odml** data model. Accordingly the *Value* entity does no longer exist. New versions of the library can read but not write old data.
* New *DataFrame* entity.
* *Tags* and *MultiTags* can link to DataFrames as features.
* *RangeDimension* can link to DataFrames as source for the ticks.
* *AliasRangeDimension* has been removed, the equivalent can be achieved with linking to a *DataArray*.

The *DataFrame*
###############

The *DataFrame* is a new entity that stored tabular data. Each column has a name, unit, and data type. (see :ref:`The DataFrame` for more information)

*RangeDimension*
################

* *RangeDimensions* ticks can now be stored within the dimension descriptor, or in linked DataArrays or DataFrames. Ticks must still be one-dimensional (see :ref:`RangeDimension` for more information).
* Because of the above change, the former *AliasRangeDimension* is no longer needed. The same functionality is achieved by linking the *RangeDimension* to the *DataArray* itself.

API changes
###########

* ``DataArray.append_alias_range_dimension`` has been removed. Use ``DataArray.append_range_dimension_using_self`` for the same effect.
* ``SampledDimension.axis`` can now be called with an optional argument ``start_position`` to get an axis that starts at the given position. Starting at a given index is still possible.
* ``Block.create_data_array`` has additional keyword-arguments to directly provide label and unit.


Misc
####

Extended command line tool abilities; The ``nixio`` command line tool now bundles commands for validating files, upgrading old files to the current version, and to explore file content.

.. code-block:: bash

   nixio --help

.. code-block:: text

   usage: nixio [-h] {explore,validate,upgrade} 

   Command line interface for nixio tools

   optional arguments:
   -h, --help            show this help message and exit

   commands:
   {explore,validate,upgrade}
      explore             Search for information within NIX file(s). Use the "file" command for general
                           information about the file(s). The verbose flag can be used to get more detailed
                           information about the file structure. Multiple -v options increase the
                           verbosity. (e.g. 'nixio explore file nix_file -vvv' for most detailed output).
                           The "metadata" (mdata) and "data" commands provide further options for finding
                           and viewing data and metadata information. With the "dump" subcommand data can
                           be dumped to file (up to 3D data). The "plot" command is only available if the
                           nixworks package is installed (https://github.com/G-node/nixworks). NOTE: This
                           tool is under active development. Please use the github issue tracker
                           (https://github.com/G-node/nixpy/issues) for bug reports and feature requests.
      validate            Validate NIX files for missing or inconsistent objects and annotations.
      upgrade             Upgrade NIX files to newest file format version.