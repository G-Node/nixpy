# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import os

import unittest
import h5py
import numpy as np

import nixio as nix
import nixio.file as filepy
from nixio.exceptions import InvalidFile


skip_cpp = not hasattr(nix, "core")


class FileTestBase(unittest.TestCase):

    testfilename = "filetest.h5"

    def setUp(self):
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)

    def tearDown(self):
        self.file.close()
        os.remove(self.testfilename)

    def test_file_format(self):
        assert(self.file.format == "nix")
        assert(self.file.version == filepy.HDF_FF_VERSION)

    def test_file_timestamps(self):
        created_at = self.file.created_at
        assert(created_at > 0)

        updated_at = self.file.updated_at
        assert(updated_at > 0)

        self.file.force_created_at(1403530068)
        assert(self.file.created_at == 1403530068)

    def test_file_blocks(self):
        assert(len(self.file.blocks) == 0)

        block = self.file.create_block("test block", "recordingsession")

        assert(len(self.file.blocks) == 1)

        assert(block in self.file.blocks)
        assert(block.id in self.file.blocks)
        assert("notexist" not in self.file.blocks)

        assert(block.id == self.file.blocks[0].id)
        assert(block.id == self.file.blocks[-1].id)

        del self.file.blocks[0]

        assert(len(self.file.blocks) == 0)

    def test_file_sections(self):
        assert(len(self.file.sections) == 0)

        section = self.file.create_section("test section", "recordingsession")

        assert(len(self.file.sections) == 1)

        assert(section in self.file.sections)
        assert(section.id in self.file.sections)
        assert("notexist" not in self.file.sections)

        assert(section.id == self.file.sections[0].id)
        assert(section.id == self.file.sections[-1].id)

        del self.file.sections[0]

        assert(len(self.file.sections) == 0)

    def test_file_find_sections(self):
        for i in range(2):
            self.file.create_section("level1-p0-s" + str(i), "dummy")
        for i in range(2):
            self.file.sections[0].create_section("level2-p1-s" + str(i),
                                                 "dummy")
        for i in range(2):
            self.file.sections[1].create_section("level2-p2-s" + str(i),
                                                 "dummy")
        for i in range(2):
            self.file.sections[0].sections[0].create_section(
                "level3-p1-s" + str(i), "dummy"
            )

        assert(len(self.file.find_sections()) == 8)
        assert(len(self.file.find_sections(limit=1)) == 2)
        assert(len(self.file.find_sections(filtr=lambda x: "level2-p1-s" in
                                                           x.name)) == 2)
        assert(len(self.file.find_sections(filtr=lambda x: "level2-p1-s" in
                                                           x.name,
                                           limit=1)) == 0)

    def test_order_tracking(self):
        blknames = []
        for idx in range(10):
            name = "block_" + str(idx)
            self.file.create_block(name, "ordertest")
            blknames.append(name)

        danames = []
        datablockname = blknames[0]
        datablock = self.file.blocks[datablockname]
        for idx in range(7):
            name = "data_" + str(idx)
            da = datablock.create_data_array(name, "thedata",
                                             data=np.array([0]))
            da.definition = "da definition"
            danames.append(name)
        self.file.close()

        self.file = nix.File.open(self.testfilename, nix.FileMode.ReadOnly)

        for idx in range(len(self.file.blocks)):
            self.assertEqual(blknames[idx], self.file.blocks[idx].name)

        datablock = self.file.blocks[datablockname]
        for idx in range(len(datablock.data_arrays)):
            self.assertEqual(danames[idx], datablock.data_arrays[idx].name)


@unittest.skipIf(skip_cpp, "HDF5 backend not available.")
class TestFileCPP(FileTestBase):

    backend = "hdf5"


class TestFilePy(FileTestBase):

    backend = "h5py"


class TestFileVerPy(unittest.TestCase):

    backend = "h5py"
    testfilename = "versiontest.h5"
    filever = filepy.HDF_FF_VERSION
    fformat = filepy.FILE_FORMAT

    def try_open(self, mode):
        f = nix.File.open(self.testfilename, mode)
        f.close()

    def set_header(self, fformat=None, version=None):
        if fformat is None:
            fformat = self.fformat
        if version is None:
            version = self.filever
        self.h5root.attrs["format"] = fformat
        self.h5root.attrs["version"] = version
        self.h5root.attrs["created_at"] = 0
        self.h5root.attrs["updated_at"] = 0
        if "data" not in self.h5root:
            self.h5root.create_group("data")
            self.h5root.create_group("metadata")

    def setUp(self):
        self.h5file = h5py.File(self.testfilename, mode="w")
        self.h5root = self.h5file["/"]

    def tearDown(self):
        self.h5file.close()
        os.remove(self.testfilename)

    def test_read_write(self):
        self.set_header()
        self.try_open(nix.FileMode.ReadWrite)

    def test_read_only(self):
        vx, vy, vz = self.filever
        roversion = (vx, vy, vz+2)
        self.set_header(version=roversion)
        self.try_open(nix.FileMode.ReadOnly)
        with self.assertRaises(RuntimeError):
            self.try_open(nix.FileMode.ReadWrite)

    def test_no_open(self):
        vx, vy, vz = self.filever
        noversion = (vx, vy+3, vz+2)
        self.set_header(version=noversion)
        with self.assertRaises(RuntimeError):
            self.try_open(nix.FileMode.ReadWrite)
        with self.assertRaises(RuntimeError):
            self.try_open(nix.FileMode.ReadOnly)
        noversion = (vx, vy+1, vz)
        self.set_header(version=noversion)
        with self.assertRaises(RuntimeError):
            self.try_open(nix.FileMode.ReadWrite)
        with self.assertRaises(RuntimeError):
            self.try_open(nix.FileMode.ReadOnly)
        noversion = (vx+1, vy, vz)
        self.set_header(version=noversion)
        with self.assertRaises(RuntimeError):
            self.try_open(nix.FileMode.ReadWrite)
        with self.assertRaises(RuntimeError):
            self.try_open(nix.FileMode.ReadOnly)

    def test_bad_tuple(self):
        self.set_header(version=(-1, -1, -1))
        with self.assertRaises(RuntimeError):
            self.try_open(nix.FileMode.ReadOnly)
        self.set_header(version=(1, 2))
        with self.assertRaises(RuntimeError):
            self.try_open(nix.FileMode.ReadOnly)

    def test_bad_format(self):
        self.set_header(fformat="NOT_A_NIX_FILE")
        with self.assertRaises(InvalidFile):
            self.try_open(nix.FileMode.ReadOnly)
