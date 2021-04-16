# -*- coding: utf-8 -*-
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
import time

import nixio as nix
import nixio.file as filepy
from nixio.exceptions import InvalidFile
from .tmp import TempDir


class TestFile(unittest.TestCase):

    def setUp(self):
        self.tmpdir = TempDir("filetest")
        self.testfilename = os.path.join(self.tmpdir.path, "filetest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)

    def tearDown(self):
        self.file.close()
        self.tmpdir.cleanup()

    def test_file_format(self):
        assert self.file.format == "nix"
        assert self.file.version == filepy.HDF_FF_VERSION

    def test_file_timestamps(self):
        created_at = self.file.created_at
        assert created_at > 0

        updated_at = self.file.updated_at
        assert updated_at > 0

        self.file.force_created_at(1403530068)
        assert self.file.created_at == 1403530068

    def test_file_blocks(self):
        assert len(self.file.blocks) == 0

        block = self.file.create_block("test block", "recordingsession")

        assert len(self.file.blocks) == 1

        assert block in self.file.blocks
        assert block.id in self.file.blocks
        assert "notexist" not in self.file.blocks

        assert block.id == self.file.blocks[0].id
        assert block.id == self.file.blocks[-1].id

        del self.file.blocks[0]

        assert len(self.file.blocks) == 0

    def test_file_sections(self):
        assert len(self.file.sections) == 0

        section = self.file.create_section("test section", "recordingsession")

        assert len(self.file.sections) == 1

        assert section in self.file.sections
        assert section.id in self.file.sections
        assert "notexist" not in self.file.sections

        assert section.id == self.file.sections[0].id
        assert section.id == self.file.sections[-1].id

        del self.file.sections[0]

        assert len(self.file.sections) == 0

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

        assert len(self.file.find_sections()) == 8
        assert len(self.file.find_sections(limit=1)) == 2
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

    def test_context_open(self):
        fname = os.path.join(self.tmpdir.path, "contextopen.nix")
        with nix.File.open(fname, nix.FileMode.Overwrite) as nf:
            nf.create_block("blocky", "test-block")

        with nix.File.open(fname, nix.FileMode.ReadOnly) as nf:
            self.assertEqual(nf.blocks[0].name, "blocky")

    def test_copy_on_file(self):
        tar_filename = os.path.join(self.tmpdir.path, "copytarget.nix")
        tar_file = nix.File.open(tar_filename, nix.FileMode.Overwrite)
        blk1 = self.file.create_block("t111t bk", "testcopy")
        blk2 = tar_file.create_block("blk2", "blk")
        blk1.create_data_array("da1", 'grp da1', data=[(1, 2, 3)])
        da2 = blk2.create_data_array("da2", 'grp da2', data=[(4, 5, 6)])
        blk2.create_multi_tag("mt2", "useless", da2)
        sec1 = self.file.create_section("test sec", 'test')
        sec1.create_section("child sec", "child")
        ori_prop = sec1.create_property("prop origin",
                                        values_or_dtype=[1, 2, 3])
        tar_file.create_block(copy_from=blk1, keep_copy_id=False)
        copied_sec = tar_file.copy_section(sec1, children=False, keep_id=True)
        assert tar_file.sections[0].name == sec1.name
        assert tar_file.blocks[1].name == blk1.name
        assert tar_file.blocks[1].data_arrays[0].name \
            == blk1.data_arrays[0].name
        assert tar_file.blocks[1].data_arrays[0].id != blk1.data_arrays[0].id
        assert tar_file.sections[0] == sec1
        assert len(self.file.find_sections()) == 2
        assert len(tar_file.find_sections()) == 1
        assert copied_sec.props[0] == ori_prop  # Properties are still there
        assert not copied_sec.sections  # children is False
        tar_file.close()
        # test copying on the same file
        self.assertRaises(NameError, self.file.create_block, copy_from=blk1)
        self.file.create_block(name="111", copy_from=blk1)
        assert self.file.blocks[0] == self.file.blocks[1]  # ID stays the same
        assert self.file.blocks[0].name != self.file.blocks[1].name

    def test_timestamp_autoupdate(self):
        # Using Block to test Entity.definition
        blk = self.file.create_block("block", "timetest")
        blktime = blk.updated_at
        time.sleep(1)  # wait for time to change
        blk.definition = "updated"
        # no update
        self.assertNotEqual(blk.updated_at, blktime)

        rblk = self.file.blocks["block"]  # read through container
        time.sleep(1)  # wait for time to change
        rblk.definition = "updated again"
        self.assertNotEqual(rblk.updated_at, blktime)

        # Using Block to test Entity.type
        blktime = blk.updated_at
        time.sleep(1)  # wait for time to change
        blk.type = "updated"
        # no update
        self.assertNotEqual(blk.updated_at, blktime)

        rblk = self.file.blocks["block"]  # read through container
        time.sleep(1)  # wait for time to change
        rblk.type = "updated again"
        self.assertNotEqual(rblk.updated_at, blktime)

    def test_timestamp_noautoupdate(self):
        # Using Block to test Entity.definition
        blk = self.file.create_block("block", "timetest")

        # disable timestamp autoupdating
        self.file.auto_update_timestamps = False
        blktime = blk.updated_at
        time.sleep(1)  # wait for time to change
        blk.definition = "update"
        self.assertEqual(blk.updated_at, blktime)

        rblk = self.file.blocks["block"]  # read through container
        rblktime = rblk.updated_at
        time.sleep(1)  # wait for time to change
        rblk.definition = "time should change"
        self.assertEqual(rblk.updated_at, rblktime)

        blktime = blk.updated_at
        time.sleep(1)  # wait for time to change
        blk.type = "update"
        self.assertEqual(blk.updated_at, blktime)

        rblk = self.file.blocks["block"]  # read through container
        rblktime = rblk.updated_at
        time.sleep(1)  # wait for time to change
        rblk.type = "time should change"
        self.assertEqual(rblk.updated_at, rblktime)


class TestFileVer(unittest.TestCase):

    backend = "h5py"
    filever = filepy.HDF_FF_VERSION
    fformat = filepy.FILE_FORMAT

    def try_open(self, mode):
        nix_file = nix.File.open(self.testfilename, mode)
        nix_file.close()

    def set_header(self, fformat=None, version=None, fileid=None):
        if fformat is None:
            fformat = self.fformat
        if version is None:
            version = self.filever
        if fileid is None:
            fileid = nix.util.create_id()
        self.h5root.attrs["format"] = fformat
        self.h5root.attrs["version"] = version
        self.h5root.attrs["id"] = fileid
        self.h5root.attrs["created_at"] = 0
        self.h5root.attrs["updated_at"] = 0
        if "data" not in self.h5root:
            self.h5root.create_group("data")
            self.h5root.create_group("metadata")

    def setUp(self):
        self.tmpdir = TempDir("vertest")
        self.testfilename = os.path.join(self.tmpdir.path, "vertest.nix")
        self.h5file = h5py.File(self.testfilename, mode="w")
        self.h5root = self.h5file["/"]

    def tearDown(self):
        self.h5file.close()
        self.tmpdir.cleanup()

    def test_read_write(self):
        self.set_header()
        self.try_open(nix.FileMode.ReadWrite)

    def test_read_only(self):
        ver_x, ver_y, ver_z = self.filever
        roversion = (ver_x, ver_y, ver_z+2)
        self.set_header(version=roversion)
        self.try_open(nix.FileMode.ReadOnly)
        with self.assertRaises(RuntimeError):
            self.try_open(nix.FileMode.ReadWrite)

    def test_no_open(self):
        ver_x, ver_y, ver_z = self.filever
        noversion = (ver_x, ver_y+3, ver_z+2)
        self.set_header(version=noversion)
        with self.assertRaises(RuntimeError):
            self.try_open(nix.FileMode.ReadWrite)
        with self.assertRaises(RuntimeError):
            self.try_open(nix.FileMode.ReadOnly)
        noversion = (ver_x, ver_y+1, ver_z)
        self.set_header(version=noversion)
        with self.assertRaises(RuntimeError):
            self.try_open(nix.FileMode.ReadWrite)
        with self.assertRaises(RuntimeError):
            self.try_open(nix.FileMode.ReadOnly)
        noversion = (ver_x+1, ver_y, ver_z)
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

    def test_bad_id(self):
        self.set_header(fileid="")
        with self.assertRaises(RuntimeError):
            self.try_open(nix.FileMode.ReadOnly)

        # empty file ID OK for versions older than 1.2.0
        self.set_header(version=(1, 1, 1), fileid="")
        self.try_open(nix.FileMode.ReadOnly)

        self.set_header(version=(1, 1, 0), fileid="")
        self.try_open(nix.FileMode.ReadOnly)

        self.set_header(version=(1, 0, 0), fileid="")
        self.try_open(nix.FileMode.ReadOnly)
