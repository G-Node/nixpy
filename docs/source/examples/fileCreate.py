#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import nixio as nix


file_name = 'file_create_example.h5'

# create a new file overwriting any existing content
file = nix.File.open(file_name, nix.FileMode.Overwrite)
print(file.format, file.version, file.created_at)

# close file
file.close()

# re-open file for read-only access
file  = nix.File.open(file_name, nix.FileMode.ReadOnly)

# this command will fail putting out HDF5 Errors
file.create_block("test block", "test")

file.close()

# re-open for read-write access
file = nix.File.open(file_name, nix.FileMode.ReadWrite)

# the following command now works fine
file.create_block("test block", "test")

file.close()






