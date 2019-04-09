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
import nixio as nix
from .tmp import TempDir


class TestBlock(unittest.TestCase):

    def setUp(self):
        self.tmpdir = TempDir("blocktest")
        self.testfilename = os.path.join(self.tmpdir.path, "blocktest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.block = self.file.create_block("test block", "recordingsession")
        self.other = self.file.create_block("other block", "recordingsession")

    def tearDown(self):
        del self.file.blocks[self.block.id]
        del self.file.blocks[self.other.id]
        self.file.close()
        self.tmpdir.cleanup()

    def test_block_eq(self):
        assert(self.block == self.block)
        assert(not self.block == self.other)
        assert(self.block is not None)

    def test_block_id(self):
        assert(self.block.id is not None)

    def test_block_name(self):
        assert(self.block.name is not None)

    def test_block_type(self):
        def set_none():
            self.block.type = None

        assert(self.block.type is not None)
        self.assertRaises(Exception, set_none)

        self.block.type = "foo type"
        assert(self.block.type == "foo type")

    def test_block_definition(self):
        assert(self.block.definition is None)

        self.block.definition = "definition"
        assert(self.block.definition == "definition")

        self.block.definition = None
        assert(self.block.definition is None)

    def test_block_timestamps(self):
        created_at = self.block.created_at
        assert(created_at > 0)

        updated_at = self.block.updated_at
        assert(updated_at > 0)

        self.block.force_created_at(1403530068)
        assert(self.block.created_at == 1403530068)

    def test_block_data_arrays(self):
        assert(len(self.block.data_arrays) == 0)

        data_array = self.block.create_data_array("test data_array",
                                                  "recordingsession",
                                                  nix.DataType.Int32, (0, ))

        assert(len(self.block.data_arrays) == 1)

        # TODO implement __eq__ for DataArray
        assert(data_array.id in self.block.data_arrays)
        assert("notexist" not in self.block.data_arrays)

        assert(data_array.id == self.block.data_arrays[0].id)
        assert(data_array.id == self.block.data_arrays[-1].id)

        del self.block.data_arrays[0]

        assert(len(self.block.data_arrays) == 0)

    def test_block_multi_tags(self):
        assert(len(self.block.multi_tags) == 0)

        data_array = self.block.create_data_array("test array",
                                                  "recording",
                                                  nix.DataType.Int32, (0, ))
        multi_tag = self.block.create_multi_tag("test multi_tag",
                                                "recordingsession", data_array)

        assert(len(self.block.multi_tags) == 1)

        # TODO implement __eq__ for MultiTag
        # assert(multi_tag in self.block.multi_tags)
        assert(multi_tag.id in self.block.multi_tags)
        assert("notexist" not in self.block.multi_tags)

        assert(multi_tag.id == self.block.multi_tags[0].id)
        assert(multi_tag.id == self.block.multi_tags[-1].id)

        del self.block.multi_tags[0]

        assert(len(self.block.multi_tags) == 0)

    def test_block_tags(self):
        assert(len(self.block.tags) == 0)

        tag = self.block.create_tag("test tag", "recordingsession", [0])

        assert(len(self.block.tags) == 1)

        assert(tag in self.block.tags)
        assert(tag.id in self.block.tags)
        assert("notexist" not in self.block.tags)

        assert(tag.id == self.block.tags[0].id)
        assert(tag.id == self.block.tags[-1].id)

        del self.block.tags[0]

        assert(len(self.block.tags) == 0)

    def test_block_sources(self):
        assert(len(self.block.sources) == 0)

        source = self.block.create_source("test source", "electrode")

        assert(len(self.block.sources) == 1)

        assert(source in self.block.sources)
        assert(source.id in self.block.sources)
        assert("notexist" not in self.block.sources)

        assert(source.id == self.block.sources[0].id)
        assert(source.id == self.block.sources[-1].id)

        del self.block.sources[0]

        assert(len(self.block.sources) == 0)

    def test_block_find_sources(self):
        for i in range(2):
            self.block.create_source("level1-p0-s" + str(i), "dummy")
        for i in range(2):
            self.block.sources[0].create_source("level2-p1-s" + str(i),
                                                "dummy")
        for i in range(2):
            self.block.sources[1].create_source("level2-p2-s" + str(i),
                                                "dummy")
        for i in range(2):
            self.block.sources[0].sources[0].create_source(
                "level3-p1-s" + str(i), "dummy"
            )

        assert(len(self.block.find_sources()) == 8)
        assert(len(self.block.find_sources(limit=1)) == 2)
        assert(len(self.block.find_sources(filtr=lambda x: "level2-p1-s" in
                                                           x.name)) == 2)
        assert(len(self.block.find_sources(filtr=lambda x: "level2-p1-s" in
                                                           x.name,
                                           limit=1)) == 0)

    def test_block_groups(self):
        assert(len(self.block.groups) == 0)

        group = self.block.create_group("test group", "RecordingChannelGroup")

        assert(len(self.block.groups) == 1)

        assert(group in self.block.groups)
        assert(group.id in self.block.groups)
        assert("notexist" not in self.block.groups)

        assert(group.id == self.block.groups[0].id)
        assert(group.id == self.block.groups[-1].id)

        del self.block.groups[0]

        assert(len(self.block.groups) == 0)

    def test_copy_on_block(self):
        tar_filename = os.path.join(self.tmpdir.path, "copytarget.nix")
        tar_file = nix.File.open(tar_filename, nix.FileMode.Overwrite)
        blk2 = tar_file.create_block("blk2", "blk")
        data = [(1, 2, 3), (4, 5, 6)]
        da = self.block.create_data_array("da1", 'grp da1', data=data)
        mt = self.block.create_multi_tag("mt1", "some mt", da)
        namelist = ['name', 'id', 'time']
        dtlist = [nix.DataType.Int64, str,
                           nix.DataType.Float]
        arr = [(1, "cat", 20.18), (2, 'dog', 20.15), (2, 'dog', 20.15)]
        df = self.block.create_data_frame('test1', 'for_test', col_names=namelist,
                                   col_dtypes=dtlist, data=arr)
        tag = self.block.create_tag("a tag", "some tag", position=(4, 5, 6))
        blk2.create_multi_tag(copy_from=mt)
        blk2.create_data_array(copy_from=da)
        blk2.create_data_frame(copy_from=df)
        blk2.create_tag(copy_from=tag)
        assert mt == blk2.multi_tags[0]
        assert da == blk2.data_arrays[0]
        assert df == blk2.data_frames[0]
        assert tag == blk2.tags[0]
        tar_file.close()
        self.block.create_data_array("da2", 'grp da2', data=[(1, 2, 3)])
        da2 = self.block.data_arrays[1]
        mt2 = self.block.multi_tags[0]
        self.assertRaises(NameError, lambda: self.block.create_data_array(
            copy_from=da2))
        self.block.create_data_array(name="new da name", copy_from=da2)
        self.block.create_multi_tag(name="new mt name", copy_from=mt2)
        assert self.block.multi_tags[0] == mt2
        assert self.block.data_arrays[1] == da2