.. toctree::
   :maxdepth: 1

File handling
=============

The *File* entity encapsulates all information of a dataset. *File*
entities keep some general information such as creation time and date,
format version etc. It is the entry-point to a *NIX* file.

File modes
----------

A *NIX* file can be opened in one of three modes:

1. ``nix.FileMode.Overwrite`` Used for creating a new file or overwriting any content
   in an existing one!
2. ``nix.FileMode.ReadWrite`` Opens a file if it exists or otherwise creates a new
   one. Does **not** overwrite existing content.
3. ``nix.FileMode.ReadOnly`` Opens an existing file. The content can not be changed.
   Will raise an error when the provided path is invalid (e.g. the file
   does not exist).

Creating a new file
--------------------

.. literalinclude:: examples/fileCreate.py
   :language: python
   :lines: 3-13
   :emphasize-lines: 7

As mentioned above, using ``nix.FileMode.Overwrite`` will destroy any existing content of the file. **By default**, if the ``FileMode`` flag is not specified, a file is opened in the ``FileMode.ReadWrite`` mode.

In this tutorial files will always have the extension ``*.nix``. This is not specified in the library and you are free to use any file extension.

Opening existing files
-----------------------

Use ``nix.FileMode.ReadWrite`` or ``nix.FileMode.ReadOnly`` to open
an existing file to work with the data. If you want to overwrite *any*
existing content in order to replace the file use
``nix.FileMode.Overwite``.

In ``ReadOnly`` mode, you cannot change the file content:

.. literalinclude:: examples/fileCreate.py
   :language: python
   :lines: 14-23

In order to change the file content the file needs to be opened in ``ReadWrite`` mode:

.. literalinclude:: examples/fileCreate.py
   :language: python
   :lines: 25-28

Trying to open an non-existing file in ``ReadOnly`` mode will lead to an
error!

.. literalinclude:: examples/fileCreate.py
   :language: python
   :lines: 31-38

Enabling compression
--------------------

By default, data stored inside a *NIX* file will not be compressed. You
can switch on compression during file opening.

.. literalinclude:: examples/fileCreate.py
   :language: python
   :lines: 39-40

Compression is handled transparently by the hdf5-library, no further
user interaction is required. Compression reduces reading and writing
performance. You can choose to switch off compression on individual
*DataArray*\ s by passing the ``nix.Compression.No`` flag at
the time of creation.
