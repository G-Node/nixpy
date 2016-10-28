# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function)#, unicode_literals)

import unittest

try:
    import nixio.core
    skip_cpp = False
except ImportError:
    skip_cpp = True

import h5py
from nixio import *
import nixio.pycore.file as filepy


class _FileTest(unittest.TestCase):

    backend = None

    def setUp(self):
        self.file = File.open("unittest.h5", FileMode.Overwrite,
                              backend=self.backend)

    def tearDown(self):
        self.file.close()

    def test_file_format(self):
        assert(self.file.format == "nix")
        assert(self.file.version == (1, 0, 0))

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

        assert(block      in self.file.blocks)
        assert(block.id   in self.file.blocks)
        assert("notexist" not in self.file.blocks)

        assert(block.id == self.file.blocks[0].id)
        assert(block.id == self.file.blocks[-1].id)

        del self.file.blocks[0]

        assert(len(self.file.blocks) == 0)

    def test_file_sections(self):
        assert(len(self.file.sections) == 0)

        section = self.file.create_section("test section", "recordingsession")

        assert(len(self.file.sections) == 1)

        assert(section      in self.file.sections)
        assert(section.id   in self.file.sections)
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


@unittest.skipIf(skip_cpp, "HDF5 backend not available.")
class FileTestCPP(_FileTest):

    backend = "hdf5"


class FileTestPy(_FileTest):

    backend = "h5py"


class FileVerTestPy(unittest.TestCase):

    backend = "h5py"
    filename = "versiontest.h5"
    filever = filepy.HDF_FF_VERSION
    format = filepy.FILE_FORMAT

    def nix_open(self, mode):
        return File.open(self.filename, mode, backend=self.backend)

    def setUp(self):
        self.h5file = h5py.File(self.filename, mode="w")

    def tearDown(self):
        self.h5file.close()

    def test_read_write(self):
        self.h5file.attrs["version"] = self.filever
        self.h5file.attrs["format"] = self.format
        self.assertTrue(self.nix_open(FileMode.ReadWrite))

    def test_read_only(self):
        vx, vy, vz = self.filever
        roversion = (vx, vy, vz+2)
        self.h5file.attrs["version"] = roversion
        with self.assertRaises(RuntimeError):
            self.nix_open(FileMode.ReadWrite)

    def test_bad_version(self):
        pass

    def test_bad_tuple(self):
        pass

    def test_bad_format(self):
        pass



