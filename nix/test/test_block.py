# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function)#, unicode_literals)

import unittest

from nix import *

class TestBlock(unittest.TestCase):

    def setUp(self):
        # TODO "unittest.h5 is a unicode string and is handed over to a c++ function expecting a string"
        # this leads to an error. if "unittest.h5".encode("utf-8") or b'unittest.h5' is used, the c++ function can handle the string
        # but is not able to create the file any longer. Should this somehow be adressed on the c++ side of the code?
        self.file  = File.open('unittest.h5', FileMode.Overwrite)
        self.block = self.file.create_block("test block", "recordingsession")
        self.other = self.file.create_block("other block", "recordingsession")

    def tearDown(self):
        del self.file.blocks[self.block.id]
        del self.file.blocks[self.other.id]
        self.file.close()

    def test_block_eq(self):
        assert(self.block == self.block)
        assert(not self.block == self.other)
        assert(not self.block == None)

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

        data_array = self.block.create_data_array("test data_array", "recordingsession", DataType.Int32, (0, ))

        assert(len(self.block.data_arrays) == 1)

        # TODO implement __eq__ for DataArray
        #assert(data_array      in self.block.data_arrays)
        assert(data_array.id   in self.block.data_arrays)
        assert("notexist" not in self.block.data_arrays)

        assert(data_array.id == self.block.data_arrays[0].id)
        assert(data_array.id == self.block.data_arrays[-1].id)

        del self.block.data_arrays[0]

        assert(len(self.block.data_arrays) == 0)

    def test_block_multi_tags(self):
        assert(len(self.block.multi_tags) == 0)

        data_array = self.block.create_data_array("test array", "recording", DataType.Int32, (0, ))
        multi_tag = self.block.create_multi_tag("test multi_tag", "recordingsession", data_array)

        assert(len(self.block.multi_tags) == 1)

        # TODO implement __eq__ for MultiTag
        #assert(multi_tag      in self.block.multi_tags)
        assert(multi_tag.id   in self.block.multi_tags)
        assert("notexist" not in self.block.multi_tags)

        assert(multi_tag.id == self.block.multi_tags[0].id)
        assert(multi_tag.id == self.block.multi_tags[-1].id)

        del self.block.multi_tags[0]

        assert(len(self.block.multi_tags) == 0)

    def test_block_tags(self):
        assert(len(self.block.tags) == 0)

        tag = self.block.create_tag("test tag", "recordingsession", [0])

        assert(len(self.block.tags) == 1)

        assert(tag      in self.block.tags)
        assert(tag.id   in self.block.tags)
        assert("notexist" not in self.block.tags)

        assert(tag.id == self.block.tags[0].id)
        assert(tag.id == self.block.tags[-1].id)

        del self.block.tags[0]

        assert(len(self.block.tags) == 0)

    def test_block_sources(self):
        assert(len(self.block.sources) == 0)

        source = self.block.create_source("test source", "electrode")

        assert(len(self.block.sources) == 1)

        assert(source      in self.block.sources)
        assert(source.id   in self.block.sources)
        assert("notexist" not in self.block.sources)

        assert(source.id == self.block.sources[0].id)
        assert(source.id == self.block.sources[-1].id)

        del self.block.sources[0]

        assert(len(self.block.sources) == 0)

    def test_block_find_sources(self):
        for i in range(2): self.block.create_source("level1-p0-s" + str(i), "dummy")
        for i in range(2): self.block.sources[0].create_source("level2-p1-s" + str(i), "dummy")
        for i in range(2): self.block.sources[1].create_source("level2-p2-s" + str(i), "dummy")
        for i in range(2): self.block.sources[0].sources[0].create_source("level3-p1-s" + str(i), "dummy")

        assert(len(self.block.find_sources()) == 8)
        assert(len(self.block.find_sources(limit=1)) == 2)
        assert(len(self.block.find_sources(filtr=lambda x : "level2-p1-s" in x.name)) == 2)
        assert(len(self.block.find_sources(filtr=lambda x : "level2-p1-s" in x.name, limit=1)) == 0)

    def test_block_groups(self):
        assert(len(self.block.groups) == 0)

        group = self.block.create_group("test group", "RecordingChannelGroup")

        assert(len(self.block.groups) == 1)

        assert(group      in self.block.groups)
        assert(group.id   in self.block.groups)
        assert("notexist" not in self.block.groups)

        assert(group.id == self.block.groups[0].id)
        assert(group.id == self.block.groups[-1].id)

        del self.block.groups[0]

        assert(len(self.block.groups) == 0)