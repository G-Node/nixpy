#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import nixio as nix
import datetime as dt

file_name = 'file_create_example.nix'

# create a new file overwriting any existing content
nixfile = nix.File.open(file_name, nix.FileMode.Overwrite)
print("Nix file: %s\n\tformat: %s\n\tversion: %s\n\tcreated at: %s" % (file_name, nixfile.format, nixfile.version,
                                                                       str(dt.datetime.fromtimestamp(nixfile.created_at))))
nixfile.close()

# re-open file for read-only access
nixfile = nix.File.open(file_name, nix.FileMode.ReadOnly)

# this command will fail putting out an error
try:
    nixfile.create_block("test block", "test")
except ValueError:
    print("Error caught: cannot create a new group in nix.FileMode.ReadOnly mode")

nixfile.close()

# re-open for read-write access, creating new entities will work
nixfile = nix.File.open(file_name, nix.FileMode.ReadWrite)
nixfile.create_block("test block", "test")
nixfile.close()

# the following file open command will fail
nonexistingfilename = "nonexistingfile.nix"

try:
    nixfile = nix.File.open(nonexistingfilename, nix.FileMode.ReadOnly)
except RuntimeError as e:
    print("Error caught: %s" % str(e))
    print("One cannot open a file, that is not existing and forbidding the library to write it.")

nixfile = nix.File.open(file_name, mode=nix.FileMode.Overwrite, compression=nix.Compression.DeflateNormal)
nixfile.close()
