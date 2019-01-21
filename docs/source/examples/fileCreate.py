#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import nixio as nix


file_name = 'file_create_example.h5'

# create a new file overwriting any existing content
nixfile = nix.File.open(file_name, nix.FileMode.Overwrite)
print(nixfile.format, nixfile.version, nixfile.created_at)

# close file
nixfile.close()

# re-open file for read-only access
nixfile = nix.File.open(file_name, nix.FileMode.ReadOnly)

# this command will fail putting out HDF5 Errors
try:
    nixfile.create_block("test block", "test")
except ValueError:
    print("Error caught: cannot create a new group in nix.FileMode.ReadOnly mode")


nixfile.close()

# re-open for read-write access
nixfile = nix.File.open(file_name, nix.FileMode.ReadWrite)

# the following command now works fine
nixfile.create_block("test block", "test")

nixfile.close()






